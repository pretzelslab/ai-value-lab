"""Decision boundaries and provenance failures, with fictional test fixtures only."""

from dataclasses import replace
from itertools import product

import pytest

from ai_value_lab import get_risk_profile
from ai_value_lab.controls import (
    DIMENSIONS,
    PAYROLL_CONTROLS,
    Control,
    EffectivenessStatus,
    ResidualReview,
    assess_residual,
)
from ai_value_lab.decision import recommend_deployment
from ai_value_lab.evidence import (
    FACTOR_NAMES,
    EvidenceAssessment,
    EvidenceFactor,
    EvidenceStatus,
    classify_confidence,
)
from ai_value_lab.models import Risk

# These references simulate reviewer inputs; they are NOT real HR evidence.
OBSERVED = EvidenceFactor(EvidenceStatus.OBSERVED, "fictional test artifact", True)


def full_evidence() -> EvidenceAssessment:
    return EvidenceAssessment("Fictional test scope", **dict.fromkeys(FACTOR_NAMES, OBSERVED))


def low_risks() -> tuple[Risk, ...]:
    return tuple(Risk(d, d, "Fictional test risk", "Low", "Low") for d in DIMENSIONS)


def reviews(level: str = "Low") -> tuple[ResidualReview, ...]:
    return tuple(
        ResidualReview(d, level, level, "Fictional reassessment", "Test reviewer", OBSERVED)
        for d in DIMENSIONS
    )


def verified_controls() -> tuple[Control, ...]:
    return tuple(replace(
        control, evidence=OBSERVED, effectiveness=EffectivenessStatus.OBSERVED, implemented=True,
    ) for control in PAYROLL_CONTROLS)


def decision(**overrides):
    inputs = {
        "monthly_value": 100, "evidence": full_evidence(),
        "risks": low_risks(), "reviews": reviews(),
    }
    inputs.update(overrides)
    return recommend_deployment(**inputs)


def test_no_evidence_is_low_with_six_explanations_and_gaps():
    result = classify_confidence(EvidenceAssessment("Payroll"))
    assert result.level == "Low"
    assert result.maturity == "No observed evidence"
    assert len(result.gaps) == 6
    assert len(result.reasons) == 7


@pytest.mark.parametrize("status", [EvidenceStatus.ASSUMED, EvidenceStatus.SYNTHETIC])
def test_nonobserved_factors_never_raise_confidence(status):
    evidence = EvidenceAssessment("Payroll", **dict.fromkeys(FACTOR_NAMES, EvidenceFactor(status)))
    assert classify_confidence(evidence).level == "Low"


@pytest.mark.parametrize("supported", list(product([False, True], repeat=6)))
def test_all_evidence_combinations_follow_gates(supported):
    factors = {
        name: OBSERVED if present else EvidenceFactor()
        for name, present in zip(FACTOR_NAMES, supported, strict=True)
    }
    result = classify_confidence(EvidenceAssessment("Test scope", **factors))
    expected = "High" if all(supported) else "Medium" if all(supported[:3]) else "Low"
    assert result.level == expected
    assert len(result.gaps) == supported.count(False)


@pytest.mark.parametrize("name", FACTOR_NAMES)
def test_inadequate_observations_lower_high_confidence(name):
    evidence = replace(full_evidence(), **{
        name: EvidenceFactor(EvidenceStatus.OBSERVED, "incomplete test coverage", False),
    })
    assert classify_confidence(evidence).level != "High"
    assert any(name in gap for gap in classify_confidence(evidence).gaps)


@pytest.mark.parametrize("kwargs", [
    {"status": "Observed"},
    {"status": EvidenceStatus.OBSERVED},
    {"status": EvidenceStatus.SYNTHETIC, "adequate": True},
    {"status": EvidenceStatus.ASSUMED, "adequate": True},
    {"adequate": "yes"},
    {"reference": None},
])
def test_invalid_evidence_is_rejected(kwargs):
    with pytest.raises((TypeError, ValueError)):
        EvidenceFactor(**kwargs)


def test_scope_and_factor_types_are_required():
    with pytest.raises(ValueError):
        EvidenceAssessment("")
    with pytest.raises(ValueError):
        EvidenceAssessment("Payroll", observed_data=True)


def test_payroll_control_set_is_small_and_explicitly_unverified():
    assert tuple(c.dimension for c in PAYROLL_CONTROLS) == DIMENSIONS
    assert all(not c.verified and not c.implemented for c in PAYROLL_CONTROLS)
    assert all(c.effectiveness == EffectivenessStatus.ASSUMED for c in PAYROLL_CONTROLS)


@pytest.mark.parametrize("changes", [
    {"name": ""}, {"purpose": " "}, {"residual_rationale": ""},
    {"dimension": "Accuracy"}, {"effectiveness": "Measured"},
    {"implemented": "yes"}, {"evidence": True},
    {"effectiveness": EffectivenessStatus.OBSERVED},
    {"effectiveness": EffectivenessStatus.OBSERVED, "evidence": OBSERVED},
    {"effectiveness": EffectivenessStatus.OBSERVED, "implemented": True},
])
def test_invalid_control_is_rejected(changes):
    with pytest.raises((TypeError, ValueError)):
        replace(PAYROLL_CONTROLS[0], **changes)


@pytest.mark.parametrize("controls", [(), PAYROLL_CONTROLS, verified_controls()])
def test_controls_alone_never_reduce_risk(controls):
    result = assess_residual(get_risk_profile("Payroll inquiry")[0], controls)
    assert result.exposure == "High"
    assert not result.evidence_supported
    assert "no control reduction" in result.rationale


def test_reduction_requires_applicable_control_and_review():
    risk = get_risk_profile("Payroll inquiry")[0]
    for controls in ((), PAYROLL_CONTROLS, verified_controls()[1:]):
        with pytest.raises(ValueError, match="evidenced applicable control"):
            assess_residual(risk, controls, reviews()[0])
    result = assess_residual(risk, verified_controls(), reviews()[0])
    assert result.exposure == "Low"
    assert result.evidence_supported
    assert result.controls == ("C1 Source-grounded review",)


def test_worsening_residual_is_preserved_without_control_credit():
    result = assess_residual(low_risks()[0], (), reviews("High")[0])
    assert result.exposure == "High"
    assert result.evidence_supported


def test_component_reduction_cannot_hide_inside_same_exposure_band():
    risk = Risk("Privacy", "Privacy", "Test", "High", "High")
    review = replace(reviews("High")[1], likelihood="Medium")
    with pytest.raises(ValueError, match="evidenced applicable control"):
        assess_residual(risk, (), review)


@pytest.mark.parametrize("changes", [
    {"dimension": "Accuracy"}, {"likelihood": "low"}, {"impact": "Critical"},
    {"rationale": ""}, {"reviewer": " "}, {"evidence": EvidenceFactor()},
    {"evidence": EvidenceFactor(EvidenceStatus.SYNTHETIC)},
])
def test_invalid_residual_review_is_rejected(changes):
    with pytest.raises(ValueError):
        replace(reviews()[0], **changes)


def test_residual_dimension_mismatch_is_rejected():
    with pytest.raises(ValueError):
        assess_residual(low_risks()[0], (), reviews()[1])
    with pytest.raises(ValueError):
        assess_residual(replace(low_risks()[0], name="Accuracy"), ())


@pytest.mark.parametrize("overrides,expected", [
    ({}, "Proceed"),
    ({"controls": verified_controls()}, "Proceed with controls"),
    ({"evidence": replace(full_evidence(), repeat_testing=EvidenceFactor())},
     "Pilot and gather evidence"),
    ({"unresolved_gaps": ("Coverage extension needed",)}, "Pilot and gather evidence"),
    ({"reviews": ()}, "Pilot and gather evidence"),
    ({"controls": PAYROLL_CONTROLS}, "Pilot and gather evidence"),
    ({"critical_gaps": ("Unauthorized data path",)}, "Restricted deployment"),
    ({"reviews": reviews("High")}, "Restricted deployment"),
    ({"monthly_value": 0}, "Restricted deployment"),
    ({"monthly_value": -1}, "Restricted deployment"),
    ({"monthly_value": None}, "Insufficient evidence"),
    ({"evidence": EvidenceAssessment("Payroll")}, "Insufficient evidence"),
])
def test_posture_rules(overrides, expected):
    result = decision(**overrides)
    assert result.posture == expected
    assert result.reasons and result.what_would_change
    assert len(result.residual_risks) == 4


def test_critical_gap_outranks_missing_evidence_and_economics():
    result = decision(
        monthly_value=None, evidence=EvidenceAssessment("Payroll"),
        critical_gaps=("Known unauthorized disclosure",),
    )
    assert result.posture == "Restricted deployment"
    assert "Known unauthorized disclosure" in result.evidence_gaps


def test_missing_economics_is_an_explicit_gap():
    result = decision(monthly_value=None)
    assert "Monthly economic value has not been supplied." in result.evidence_gaps


def test_inherent_high_without_controls_cannot_proceed_after_unchanged_review():
    result = decision(
        risks=get_risk_profile("Payroll inquiry"), reviews=(), controls=(),
    )
    assert result.posture == "Pilot and gather evidence"
    assert any("no required control" in gap for gap in result.evidence_gaps)


def test_high_confidence_does_not_mean_low_risk():
    result = decision(reviews=reviews("High"))
    assert result.confidence.level == "High"
    assert result.posture == "Restricted deployment"


def test_medium_residual_requires_an_applicable_control():
    result = decision(reviews=reviews("Medium"))
    assert result.posture == "Pilot and gather evidence"
    result = decision(reviews=reviews("Medium"), controls=verified_controls())
    assert result.posture == "Proceed with controls"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), True, "100"])
def test_invalid_economic_decision_input(value):
    with pytest.raises(ValueError):
        decision(monthly_value=value)


@pytest.mark.parametrize("overrides", [
    {"risks": low_risks()[:3]},
    {"risks": (low_risks()[0],) * 4},
    {"controls": (PAYROLL_CONTROLS[0],) * 2},
    {"reviews": (reviews()[0],) * 2},
    {"unresolved_gaps": ("",)},
    {"critical_gaps": "a string is not a collection of gap records"},
])
def test_incomplete_or_ambiguous_decision_inputs_rejected(overrides):
    with pytest.raises(ValueError):
        decision(**overrides)


def test_decision_is_deterministic_and_returns_control_trace():
    first = decision(controls=PAYROLL_CONTROLS, reviews=())
    assert first == decision(controls=PAYROLL_CONTROLS, reviews=())
    assert first.required_controls == tuple(c.name for c in PAYROLL_CONTROLS)
    assert any("C1" in gap for gap in first.evidence_gaps)

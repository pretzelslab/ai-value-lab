"""Display-only labels and inference: no new assessment thresholds."""

import pytest

from ai_value_lab import (
    AIInputs,
    AssuranceInputs,
    BaselineInputs,
    calculate_ai_scenario,
    calculate_baseline,
)
from ai_value_lab.presentation import (
    automation_scope,
    calculation_example,
    configuration_summary,
    decision_scope,
    decision_signal,
    economic_inference,
    economic_signal,
    executive_readout,
    highest_exposure,
    next_action,
    risk_inference,
    scope_actions,
    summary_inference,
)


@pytest.mark.parametrize("posture,signal", [
    ("Proceed", "GO"), ("Proceed with controls", "GO WITH CONTROLS"),
    ("Pilot and gather evidence", "PILOT"), ("Restricted deployment", "LIMITED"),
    ("Insufficient evidence", "HOLD FOR EVIDENCE"),
])
def test_exact_signal_mapping(posture, signal):
    assert decision_signal(posture) == signal
    assert next_action(posture)
    assert summary_inference(100, posture)


@pytest.mark.parametrize("function", [decision_signal, next_action])
def test_unknown_posture_is_not_silently_mapped(function):
    with pytest.raises(ValueError, match="Unknown deployment posture"):
        function("Unknown")


@pytest.mark.parametrize("value,signal", [
    (28420, "Positive"), (0.000001, "Positive"), (0, "Marginal"),
    (-0.000001, "Negative"), (-1000, "Negative"),
])
def test_economic_sign_without_invented_tolerance(value, signal):
    assert economic_signal(value) == signal
    assert "assumptions" in economic_inference(value)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_economics_rejected(value):
    with pytest.raises(ValueError):
        economic_signal(value)


def test_break_even_is_explained_without_precision_claim():
    assert "exactly zero" in economic_inference(0)


def test_default_summary_connects_positive_value_to_missing_evidence():
    text = summary_inference(28837.5, "Insufficient evidence")
    assert "attractive under current assumptions" in text
    assert "insufficient evidence to support deployment" in text
    assert "validate proposed controls" in next_action("Insufficient evidence")


def test_summary_changes_with_economics_and_formal_posture():
    assert "negative" in summary_inference(-1, "Restricted deployment")
    assert "block broad deployment" in summary_inference(-1, "Restricted deployment")
    assert "break-even" in summary_inference(0, "Restricted deployment")
    assert "bounded evaluation" in summary_inference(100, "Pilot and gather evidence")
    assert "retaining the assessed controls" in summary_inference(100, "Proceed with controls")


@pytest.mark.parametrize("exposures,expected", [
    (("Low", "Low", "Low", "Low"), "Low"),
    (("Low", "Medium", "Low", "Low"), "Medium"),
    (("Low", "Medium", "High", "Low"), "High"),
])
def test_risk_display_is_highest_dimension_not_new_score(exposures, expected):
    assert highest_exposure(exposures) == expected


@pytest.mark.parametrize("exposures", [(), ("Critical",), ("low",)])
def test_invalid_exposure_rejected(exposures):
    with pytest.raises(ValueError):
        highest_exposure(exposures)


def test_risk_inference_keeps_risk_confidence_and_maturity_distinct():
    text = risk_inference(("High",) * 4, "Low", "No observed evidence")
    assert "High is the highest inherent exposure (4 of 4 dimensions)" in text
    assert "confidence is Low" in text
    assert "No observed evidence" in text


@pytest.mark.parametrize("adoption,retained", [(0, 1), (0.7, 0.3), (1, 0)])
def test_automation_shares_keep_review_denominator(adoption, retained):
    result = automation_scope(adoption, 0.3)
    assert result["AI assisted share"] == adoption
    assert result["Human retained share"] == pytest.approx(retained)
    assert result["Human review rate"] == 0.3


@pytest.mark.parametrize("adoption,review", [(-0.1, 0), (1.1, 0), (0.5, -1), (0.5, 2),
                                           (float("nan"), 0), (0, float("inf"))])
def test_invalid_automation_shares_rejected(adoption, review):
    with pytest.raises(ValueError):
        automation_scope(adoption, review)


@pytest.mark.parametrize("posture", [
    "Proceed", "Proceed with controls", "Pilot and gather evidence",
    "Restricted deployment", "Insufficient evidence",
])
def test_decision_scope_retains_actual_configuration_and_advisory_boundaries(posture):
    text = decision_scope(posture, 0.7, 0.3)
    assert "70% of monthly cases" in text
    assert "30% of assisted cases" in text
    assert all(scope_actions(posture))
    assert "No AI-assisted cases configured" in decision_scope(posture, 0, 0.3)


def test_full_adoption_does_not_imply_autonomous_deployment():
    text = decision_scope("Proceed", 1, 1)
    assert "100% of monthly cases AI assisted" in text
    assert "100% of assisted cases configured for human review" in text
    assert "autonomous" not in text


def test_insufficient_evidence_is_not_permanent_rejection():
    proceed, retained = scope_actions("Insufficient evidence")
    assert "not permanent rejection" in proceed
    assert "separately approved evaluation" in proceed
    assert "not identified particular activities as safe" in retained
    assert "HOLD FOR EVIDENCE" == decision_signal("Insufficient evidence")


def test_pilot_scope_is_not_an_invented_pilot_percentage():
    assert "pilot size not yet set" in decision_scope("Pilot and gather evidence", 0.7, 0.3)


@pytest.mark.parametrize("category,adoption,confidence,posture", [
    ("Payroll inquiry", 0.7, "Low", "Insufficient evidence"),
    ("Benefits", 0.4, "Medium", "Pilot and gather evidence"),
    ("Employee data", 1, "High", "Proceed with controls"),
    ("General HR policy", 0, "Low", "Restricted deployment"),
])
def test_executive_readout_tracks_configuration(category, adoption, confidence, posture):
    text = executive_readout(
        category, 100, AIInputs(adoption_rate=adoption), ("High",) * 4,
        confidence, "Test maturity", posture,
    )
    assert category in text
    assert f"{adoption:.0%} of monthly cases" in text
    assert f"confidence is {confidence}" in text
    assert f"Formal posture: {posture}" in text
    assert "Test maturity" in text and "Next action:" in text


def test_executive_readout_withholds_broad_deployment_without_banning_all_ai():
    text = executive_readout(
        "Payroll inquiry", 28837.5, AIInputs(), ("High",) * 4,
        "Low", "No observed evidence", "Insufficient evidence",
    )
    assert "$28,837.50/month" in text
    assert "Broad deployment is not yet supported" in text
    assert "no specific tasks are identified as safe" in text


def test_configuration_summary_uses_live_inputs_and_actual_maturity():
    summary = configuration_summary(
        "Benefits", BaselineInputs(monthly_cases=2000),
        AIInputs(adoption_rate=0.4, human_review_rate=1, ai_error_rate=0.1),
        AssuranceInputs(control_effectiveness=0.5), "Covered observations",
    )
    assert summary == {
        "Use case": "Benefits", "Monthly cases": "2,000", "AI assisted share": "40%",
        "Human review rate": "100% of AI-assisted cases", "AI error assumption": "10%",
        "Control effectiveness": "50% assumed", "Evidence maturity": "Covered observations",
    }


@pytest.mark.parametrize("cases,adoption,error", [(10000, 0.7, 0.06), (5000, 0.4, 0.1), (100, 0, 0)])
def test_calculation_example_formats_current_engine_results(cases, adoption, error):
    inputs = BaselineInputs(monthly_cases=cases)
    ai = AIInputs(adoption_rate=adoption, ai_error_rate=error)
    result = calculate_ai_scenario(inputs, ai)
    lines = calculation_example(inputs, ai, calculate_baseline(inputs), result)
    text = " ".join(lines)
    assert f"{cases:,} monthly cases" in text
    assert f"{result.adopted_cases:,.2f} AI-assisted cases" in text
    assert f"{result.ai_rework_cases:,.2f} expected AI error cases" in text
    assert f"${result.monthly_savings:,.2f} monthly value before assurance" in text
    assert "User-supplied assumptions" in text and "derived" in text

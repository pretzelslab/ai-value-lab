"""Progression displays use fictional framework results, not real HR evidence."""

from dataclasses import replace

import pytest

from ai_value_lab.controls import DIMENSIONS, PAYROLL_CONTROLS, EffectivenessStatus, ResidualReview
from ai_value_lab.decision import recommend_deployment
from ai_value_lab.evidence import FACTOR_NAMES, EvidenceAssessment, EvidenceFactor, EvidenceStatus
from ai_value_lab.models import Risk
from ai_value_lab.progression import (
    POSTURE_GUIDE,
    assessment_path,
    illustrative_progression,
    progression_readout,
)

OBSERVED = EvidenceFactor(EvidenceStatus.OBSERVED, "fictional fixture only", True)


def result_for(stage, **overrides):
    count = {"hold": 0, "pilot": 3, "controlled": 6, "go": 6}[stage]
    inputs = {
        "monthly_value": 100,
        "evidence": EvidenceAssessment("Fictional scope", **dict.fromkeys(FACTOR_NAMES[:count], OBSERVED)),
        "risks": tuple(Risk(d, d, "Fictional risk", "Low", "Low") for d in DIMENSIONS),
        "reviews": tuple(ResidualReview(d, "Low", "Low", "Fictional review", "Tester", OBSERVED)
                      for d in DIMENSIONS) if count == 6 else (),
        "controls": tuple(replace(c, evidence=OBSERVED, implemented=True,
                               effectiveness=EffectivenessStatus.OBSERVED)
                       for c in PAYROLL_CONTROLS) if stage == "controlled" else (),
    }
    inputs.update(overrides)
    return recommend_deployment(**inputs)


@pytest.mark.parametrize("stage,signal,target", [
    ("hold", "HOLD FOR EVIDENCE", "PILOT"),
    ("pilot", "PILOT", "GO WITH CONTROLS"),
    ("controlled", "GO WITH CONTROLS", "Maintain GO WITH CONTROLS"),
    ("go", "GO", "Maintain GO"),
])
def test_targets_describe_actual_engine_postures(stage, signal, target):
    result = result_for(stage)
    path = assessment_path(result, 100)
    assert path.current_posture == result.posture
    assert path.signal == signal
    assert path.target.startswith(target)
    assert set(result.evidence_gaps) <= set(path.needed)
    assert "conditional" in progression_readout(path)


def test_hold_checklist_preserves_gaps_without_crediting_assumptions():
    result = result_for("hold", controls=PAYROLL_CONTROLS)
    path = assessment_path(result, 100)
    assert path.satisfied == ("Positive modeled economics under current assumptions",)
    assert any("observed_data" in gap for gap in path.needed)
    assert any("Privacy" in gap for gap in path.needed)
    assert any("effectiveness" in gap for gap in path.needed)
    assert any("residual exposure is unverified" in gap for gap in path.needed)
    assert path.needed[0] in path.next_action


def test_pilot_credits_only_supported_factors():
    path = assessment_path(result_for("pilot"), 100)
    assert any("Representative scenarios" in item for item in path.satisfied)
    assert any("repeat_testing" in item for item in path.needed)
    assert not any("Repeat testing" in item for item in path.satisfied)


def test_controlled_does_not_encourage_removal_of_required_controls():
    path = assessment_path(result_for("controlled"), 100)
    assert not path.needed
    assert "separately reassessed" in path.target
    assert "Retain assessed safeguards" in path.next_action
    assert sum("implementation and effectiveness" in item for item in path.satisfied) == 4


@pytest.mark.parametrize("value", [0, -100])
def test_nonpositive_economics_restricts_even_without_evidence(value):
    path = assessment_path(result_for("hold", monthly_value=value), value)
    assert path.signal == "LIMITED"
    assert "no next posture predicted" in path.target
    assert "non-positive economics" in path.next_action
    assert not path.satisfied


def test_critical_blocker_is_priority_over_missing_evidence():
    path = assessment_path(result_for("hold", critical_gaps=("Privacy incident unresolved",)), 100)
    assert path.signal == "LIMITED"
    assert path.primary_reason == "Critical: Privacy incident unresolved"
    assert "Privacy incident unresolved" in path.next_action


def test_evidenced_high_residual_is_not_hidden_by_supported_review():
    reviews = tuple(ResidualReview(d, "High", "High", "Fictional concern", "Tester", OBSERVED)
                    for d in DIMENSIONS)
    path = assessment_path(result_for("go", reviews=reviews), 100)
    assert path.signal == "LIMITED"
    assert "evidenced High residual" in path.next_action
    assert any("exposure High" in item for item in path.satisfied)


def test_missing_economics_is_not_credited():
    path = assessment_path(result_for("go", monthly_value=None), None)
    assert path.signal == "HOLD FOR EVIDENCE"
    assert not any("Positive modeled" in item for item in path.satisfied)
    assert "not been supplied" in path.next_action


def test_pure_go_explanation_preserves_existing_conditions():
    text = POSTURE_GUIDE[4]
    assert all(term in text for term in ("positive value", "High confidence", "Low residual",
                                        "no open gaps", "no required controls"))


def test_illustration_cannot_change_live_result():
    live = result_for("hold")
    before = assessment_path(live, 100)
    stages = illustrative_progression()
    assert [stage for stage, _ in stages] == ["Stage 1 · HOLD FOR EVIDENCE", "Stage 2 · PILOT",
                                            "Stage 3 · GO WITH CONTROLS"]
    assert "Hypothetically" in stages[1][1] and "Hypothetically" in stages[2][1]
    assert assessment_path(live, 100) == before
    assert live.confidence.level == "Low"

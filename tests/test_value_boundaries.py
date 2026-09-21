"""Economic boundary contracts; formulas are intentionally unchanged."""

from dataclasses import replace

import pytest

from ai_value_lab import (
    AIInputs,
    AssuranceInputs,
    BaselineInputs,
    calculate_ai_scenario,
    calculate_assurance,
    calculate_baseline,
    get_risk_profile,
)
from ai_value_lab.controls import PAYROLL_CONTROLS
from ai_value_lab.decision import recommend_deployment
from ai_value_lab.evidence import EvidenceAssessment


def test_no_adoption_preserves_baseline_and_has_no_payback():
    baseline = BaselineInputs()
    result = calculate_ai_scenario(baseline, AIInputs(adoption_rate=0))
    assert result.total_monthly_cost == calculate_baseline(baseline).total_monthly_cost
    assert result.adopted_cases == result.ai_rework_cases == result.ai_service_cost == 0
    assert result.monthly_savings == 0
    assert result.payback_months is None


def test_full_adoption_and_time_savings_floor():
    ai = AIInputs(adoption_rate=1, minutes_saved_per_adopted_case=10)
    result = calculate_ai_scenario(BaselineInputs(), ai)
    assert result.non_adopted_cases == 0
    assert result == calculate_ai_scenario(
        BaselineInputs(), replace(ai, minutes_saved_per_adopted_case=100),
    )
    assert result.human_hours > 0  # Review and rework remain after direct work hits zero.


def test_negative_savings_has_no_payback():
    result = calculate_ai_scenario(BaselineInputs(), AIInputs(ai_cost_per_adopted_case=100))
    assert result.monthly_savings < 0
    assert result.payback_months is None


def test_zero_implementation_cost_has_zero_payback_when_savings_positive():
    result = calculate_ai_scenario(BaselineInputs(), AIInputs(implementation_cost=0))
    assert result.payback_months == 0


@pytest.mark.parametrize("effectiveness", [0, 1])
def test_assurance_endpoints_and_conservation(effectiveness):
    ai = calculate_ai_scenario(BaselineInputs(), AIInputs())
    result = calculate_assurance(ai, AssuranceInputs(effectiveness, 1000))
    assert result.prevented_error_cases == pytest.approx(ai.ai_rework_cases * effectiveness)
    assert result.remaining_error_cases + result.prevented_error_cases == pytest.approx(
        ai.ai_rework_cases,
    )
    assert result.remaining_rework_cost + result.avoided_rework_cost == pytest.approx(
        ai.ai_rework_cost,
    )
    assert result.net_assurance_value == pytest.approx(ai.ai_rework_cost * effectiveness - 1000)


def test_no_errors_means_control_cost_only():
    ai = calculate_ai_scenario(BaselineInputs(), AIInputs(ai_error_rate=0))
    result = calculate_assurance(ai, AssuranceInputs())
    assert result.avoided_rework_cost == 0
    assert result.net_assurance_value == -1000


@pytest.mark.parametrize("rate", ["adoption_rate", "human_review_rate", "ai_error_rate"])
@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_invalid_ai_rates(rate, value):
    with pytest.raises(ValueError):
        calculate_ai_scenario(BaselineInputs(), replace(AIInputs(), **{rate: value}))


@pytest.mark.parametrize("cases", [0, -1])
def test_nonpositive_case_volume(cases):
    with pytest.raises(ValueError):
        calculate_baseline(BaselineInputs(monthly_cases=cases))


@pytest.mark.parametrize("assurance", [
    AssuranceInputs(-0.01, 0), AssuranceInputs(1.01, 0), AssuranceInputs(0.5, -1),
])
def test_invalid_assurance_inputs(assurance):
    with pytest.raises(ValueError):
        calculate_assurance(calculate_ai_scenario(BaselineInputs(), AIInputs()), assurance)


def test_payroll_worked_example_matches_documented_values_and_posture():
    baseline = calculate_baseline(BaselineInputs())
    ai = calculate_ai_scenario(BaselineInputs(), AIInputs())
    assurance = calculate_assurance(ai, AssuranceInputs())
    assert baseline.total_monthly_cost == pytest.approx(78600)
    assert ai.total_monthly_cost == pytest.approx(50180)
    assert ai.monthly_savings == pytest.approx(28420)
    assert ai.annual_savings == pytest.approx(341040)
    assert ai.payback_months == pytest.approx(50000 / 28420)
    assert assurance.net_assurance_value == pytest.approx(417.5)
    monthly_value = ai.monthly_savings + assurance.net_assurance_value
    assert monthly_value == pytest.approx(28837.5)
    decision = recommend_deployment(
        monthly_value=monthly_value,
        evidence=EvidenceAssessment("Payroll inquiry; illustrative monthly HR workflow"),
        risks=get_risk_profile("Payroll inquiry"), controls=PAYROLL_CONTROLS,
        unresolved_gaps=("Full C1-C4 control cost and review effort are unobserved.",),
    )
    assert decision.posture == "Insufficient evidence"
    assert decision.confidence.level == "Low"
    assert all(r.exposure == "High" and not r.evidence_supported for r in decision.residual_risks)

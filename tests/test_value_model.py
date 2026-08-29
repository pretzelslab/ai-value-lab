import pytest

from ai_value_lab import (
    AIInputs,
    AssuranceInputs,
    BaselineInputs,
    calculate_ai_scenario,
    calculate_assurance,
    calculate_baseline,
)


def test_baseline_calculation() -> None:
    inputs = BaselineInputs(
        monthly_cases=10_000,
        minutes_per_case=10,
        hourly_cost=45,
        rework_rate=0.08,
        rework_minutes=6,
    )

    result = calculate_baseline(inputs)

    assert result.direct_labor_hours == pytest.approx(1666.6667, rel=1e-4)
    assert result.direct_labor_cost == pytest.approx(75_000)
    assert result.rework_cost == pytest.approx(3_600)
    assert result.total_monthly_cost == pytest.approx(78_600)
    assert result.cost_per_case == pytest.approx(7.86)


def test_default_ai_scenario_creates_positive_value() -> None:
    baseline = BaselineInputs()
    ai = AIInputs()

    result = calculate_ai_scenario(baseline, ai)

    assert result.total_monthly_cost < calculate_baseline(baseline).total_monthly_cost
    assert result.monthly_savings > 0
    assert result.payback_months is not None


def test_invalid_rate_is_rejected() -> None:
    with pytest.raises(ValueError):
        calculate_ai_scenario(BaselineInputs(), AIInputs(adoption_rate=1.1))


def test_ai_rework_is_calculated() -> None:
    baseline = BaselineInputs(
        monthly_cases=10_000,
        minutes_per_case=10,
        hourly_cost=45,
        rework_rate=0.08,
        rework_minutes=6,
    )

    ai = AIInputs(
        adoption_rate=0.70,
        ai_error_rate=0.06,
        ai_rework_minutes=6,
    )

    result = calculate_ai_scenario(baseline, ai)

    assert result.ai_rework_cases == pytest.approx(420)
    assert result.ai_rework_hours == pytest.approx(42)
    assert result.ai_rework_cost == pytest.approx(1_890)


def test_assurance_value_is_calculated() -> None:
    baseline = BaselineInputs()
    ai = AIInputs()
    assurance = AssuranceInputs(
        control_effectiveness=0.75,
        control_cost=1_000,
    )

    ai_result = calculate_ai_scenario(baseline, ai)
    result = calculate_assurance(ai_result, assurance)

    assert result.prevented_error_cases == pytest.approx(315)
    assert result.remaining_error_cases == pytest.approx(105)
    assert result.avoided_rework_cost == pytest.approx(1_417.50)
    assert result.remaining_rework_cost == pytest.approx(472.50)
    assert result.control_cost == pytest.approx(1_000)
    assert result.net_assurance_value == pytest.approx(417.50)

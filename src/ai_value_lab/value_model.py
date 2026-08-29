from .models import (
    AIInputs,
    AIResult,
    AssuranceInputs,
    AssuranceResult,
    BaselineInputs,
    BaselineResult,
)


def _validate_rate(name: str, value: float) -> None:
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1. Received {value}.")


def _validate_non_negative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} cannot be negative. Received {value}.")


def validate_baseline(inputs: BaselineInputs) -> None:
    if inputs.monthly_cases <= 0:
        raise ValueError("monthly_cases must be greater than 0.")
    for name in ("minutes_per_case", "hourly_cost", "rework_minutes"):
        _validate_non_negative(name, getattr(inputs, name))
    _validate_rate("rework_rate", inputs.rework_rate)


def validate_ai(inputs: AIInputs) -> None:
    for name in ("adoption_rate", "human_review_rate", "ai_error_rate"):
        _validate_rate(name, getattr(inputs, name))
    for name in (
        "minutes_saved_per_adopted_case",
        "review_minutes",
        "ai_cost_per_adopted_case",
        "ai_rework_minutes",
        "implementation_cost",
    ):
        _validate_non_negative(name, getattr(inputs, name))


def validate_assurance(inputs: AssuranceInputs) -> None:
    _validate_rate("control_effectiveness", inputs.control_effectiveness)
    _validate_non_negative("control_cost", inputs.control_cost)


def calculate_baseline(inputs: BaselineInputs) -> BaselineResult:
    validate_baseline(inputs)

    direct_labor_hours = inputs.monthly_cases * inputs.minutes_per_case / 60
    direct_labor_cost = direct_labor_hours * inputs.hourly_cost

    rework_hours = inputs.monthly_cases * inputs.rework_rate * inputs.rework_minutes / 60
    rework_cost = rework_hours * inputs.hourly_cost

    total_monthly_cost = direct_labor_cost + rework_cost
    cost_per_case = total_monthly_cost / inputs.monthly_cases

    return BaselineResult(
        direct_labor_hours=direct_labor_hours,
        direct_labor_cost=direct_labor_cost,
        rework_hours=rework_hours,
        rework_cost=rework_cost,
        total_monthly_cost=total_monthly_cost,
        cost_per_case=cost_per_case,
    )


def calculate_ai_scenario(baseline: BaselineInputs, ai: AIInputs) -> AIResult:
    validate_baseline(baseline)
    validate_ai(ai)

    adopted_cases = baseline.monthly_cases * ai.adoption_rate
    non_adopted_cases = baseline.monthly_cases - adopted_cases

    adopted_case_minutes = max(
        baseline.minutes_per_case - ai.minutes_saved_per_adopted_case,
        0,
    )

    non_adopted_minutes = non_adopted_cases * baseline.minutes_per_case
    adopted_minutes = adopted_cases * adopted_case_minutes
    review_minutes = adopted_cases * ai.human_review_rate * ai.review_minutes

    non_adopted_rework_minutes = (
        non_adopted_cases * baseline.rework_rate * baseline.rework_minutes
    )
    ai_rework_cases = adopted_cases * ai.ai_error_rate
    ai_rework_total_minutes = ai_rework_cases * ai.ai_rework_minutes
    ai_rework_hours = ai_rework_total_minutes / 60
    ai_rework_cost = ai_rework_hours * baseline.hourly_cost

    total_human_minutes = (
        non_adopted_minutes
        + adopted_minutes
        + review_minutes
        + non_adopted_rework_minutes
        + ai_rework_total_minutes
    )

    human_hours = total_human_minutes / 60
    human_cost = human_hours * baseline.hourly_cost
    ai_service_cost = adopted_cases * ai.ai_cost_per_adopted_case
    total_monthly_cost = human_cost + ai_service_cost
    cost_per_case = total_monthly_cost / baseline.monthly_cases

    baseline_result = calculate_baseline(baseline)
    monthly_savings = baseline_result.total_monthly_cost - total_monthly_cost
    annual_savings = monthly_savings * 12
    payback_months = (
        ai.implementation_cost / monthly_savings if monthly_savings > 0 else None
    )

    return AIResult(
        adopted_cases=adopted_cases,
        non_adopted_cases=non_adopted_cases,
        ai_rework_cases=ai_rework_cases,
        ai_rework_hours=ai_rework_hours,
        ai_rework_cost=ai_rework_cost,
        human_hours=human_hours,
        human_cost=human_cost,
        ai_service_cost=ai_service_cost,
        total_monthly_cost=total_monthly_cost,
        cost_per_case=cost_per_case,
        monthly_savings=monthly_savings,
        annual_savings=annual_savings,
        payback_months=payback_months,
    )



def calculate_assurance(
    ai_result: AIResult,
    assurance: AssuranceInputs,
) -> AssuranceResult:
    validate_assurance(assurance)

    prevented_error_cases = (
        ai_result.ai_rework_cases * assurance.control_effectiveness
    )

    remaining_error_cases = (
        ai_result.ai_rework_cases - prevented_error_cases
    )

    avoided_rework_cost = (
        ai_result.ai_rework_cost * assurance.control_effectiveness
    )

    remaining_rework_cost = (
        ai_result.ai_rework_cost - avoided_rework_cost
    )

    net_assurance_value = (
        avoided_rework_cost - assurance.control_cost
    )

    return AssuranceResult(
        prevented_error_cases=prevented_error_cases,
        remaining_error_cases=remaining_error_cases,
        avoided_rework_cost=avoided_rework_cost,
        remaining_rework_cost=remaining_rework_cost,
        control_cost=assurance.control_cost,
        net_assurance_value=net_assurance_value,
    )

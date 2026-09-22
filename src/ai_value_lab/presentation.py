"""Plain-language display helpers; these never select a deployment posture."""

from math import isfinite

from .models import AIInputs, AIResult, AssuranceInputs, BaselineInputs, BaselineResult

SIGNALS = {
    "Proceed": "GO",
    "Proceed with controls": "GO WITH CONTROLS",
    "Pilot and gather evidence": "PILOT",
    "Restricted deployment": "LIMITED",
    "Insufficient evidence": "HOLD FOR EVIDENCE",
}

NEXT_ACTIONS = {
    "Proceed": "Confirm accountable approval for the assessed scope; reassess when conditions change.",
    "Proceed with controls": "Confirm control ownership and approval; retain the assessed controls.",
    "Pilot and gather evidence": "Define a bounded, separately approved evaluation and close the evidence gaps.",
    "Restricted deployment": "Resolve the stated blockers and review restrictions before considering deployment.",
    "Insufficient evidence": "Run representative evaluations, validate proposed controls, complete residual "
    "risk review, then reassess deployment posture.",
}


def decision_signal(posture: str) -> str:
    try:
        return SIGNALS[posture]
    except KeyError as exc:
        raise ValueError(f"Unknown deployment posture: {posture}") from exc


def next_action(posture: str) -> str:
    decision_signal(posture)
    return NEXT_ACTIONS[posture]


def economic_signal(monthly_value: float) -> str:
    if not isfinite(monthly_value):
        raise ValueError("Economic value must be finite.")
    if monthly_value > 0:
        return "Positive"
    if monthly_value < 0:
        return "Negative"
    return "Marginal"


def economic_inference(monthly_value: float) -> str:
    signal = economic_signal(monthly_value)
    if signal == "Marginal":
        return "Break-even under current assumptions: monthly value is exactly zero."
    if signal == "Positive":
        return "Positive economic case under current assumptions: modeled monthly savings exceed zero."
    return "Negative economic case under current assumptions: modeled monthly costs exceed benefits."


def highest_exposure(exposures: tuple[str, ...]) -> str:
    """Display the highest supplied category; no averaging or composite score."""
    levels = {"Low": 1, "Medium": 2, "High": 3}
    if not exposures or any(value not in levels for value in exposures):
        raise ValueError("Supply valid Low, Medium or High exposures.")
    return max(exposures, key=levels.__getitem__)


def risk_inference(exposures: tuple[str, ...], confidence: str, maturity: str) -> str:
    highest = highest_exposure(exposures)
    count = exposures.count(highest)
    return (
        f"{highest} is the highest inherent exposure ({count} of {len(exposures)} dimensions). "
        f"Assessment confidence is {confidence}; evidence maturity: {maturity}."
    )


def summary_inference(monthly_value: float, posture: str) -> str:
    decision_signal(posture)
    economic = {
        "Positive": "The economic case is attractive under current assumptions",
        "Marginal": "The economic case is at break-even under current assumptions",
        "Negative": "The economic case is negative under current assumptions",
    }[economic_signal(monthly_value)]
    conclusion = {
        "Proceed": "the framework supports proceeding within the assessed scope, subject to approval",
        "Proceed with controls": "proceeding depends on retaining the assessed controls and approval",
        "Pilot and gather evidence": "remaining gaps call for a bounded evaluation before broader use",
        "Restricted deployment": "the stated constraints block broad deployment",
        "Insufficient evidence": "there is currently insufficient evidence to support deployment "
        "of the configured scope; narrower, human-reviewed options need separate evaluation",
    }[posture]
    return f"{economic}, but {conclusion}." if posture != "Proceed" else f"{economic}; {conclusion}."


def automation_scope(adoption_rate: float, review_rate: float) -> dict[str, float]:
    """Shares of cases, not autonomous task coverage or shares of labor removed."""
    for rate in (adoption_rate, review_rate):
        if not isfinite(rate) or not 0 <= rate <= 1:
            raise ValueError("Adoption and review rates must be between zero and one.")
    return {
        "AI assisted share": adoption_rate,
        "Human retained share": 1 - adoption_rate,
        "Human review rate": review_rate,
    }


def decision_scope(posture: str, adoption_rate: float, review_rate: float) -> str:
    decision_signal(posture)
    automation_scope(adoption_rate, review_rate)
    if adoption_rate == 0:
        return "No AI-assisted cases configured; define a candidate scope before deployment review."
    configured = (
        f"{adoption_rate:.0%} of monthly cases AI assisted; "
        f"{review_rate:.0%} of assisted cases configured for human review"
    )
    prefix = {
        "Proceed": "Configured AI-assisted scope",
        "Proceed with controls": "Configured AI-assisted scope with required controls",
        "Pilot and gather evidence": "Proposed pilot within the configured scope; pilot size not yet set",
        "Restricted deployment": "Restrictions on the configured AI-assisted scope",
        "Insufficient evidence": "Evidence readiness of the configured AI-assisted scope",
    }[posture]
    return f"{prefix}: {configured}."


def scope_actions(posture: str) -> tuple[str, str]:
    """Advisory boundaries, not task-level permission or a second decision engine."""
    decision_signal(posture)
    proceed = {
        "Proceed": "Seek accountable approval to use AI within the assessed configuration.",
        "Proceed with controls": "Seek approval for the assessed configuration with required controls in place.",
        "Pilot and gather evidence": "Design a bounded evaluation for separate approval; define its tasks and safeguards.",
        "Restricted deployment": "Investigate blockers and design mitigations; any narrower use needs separate review.",
        "Insufficient evidence": "Plan representative evaluations. Limited or human-reviewed assistance may be "
        "explored through a separately approved evaluation; this is not permanent rejection of AI.",
    }[posture]
    restricted = (
        "Retain the configured human review and all required action gates. Unassessed activities "
        "and autonomous payroll changes are outside this recommendation."
        if posture in {"Proceed", "Proceed with controls"}
        else "Do not expand AI use based on this result. Keep consequential actions under human "
        "control; the framework has not identified particular activities as safe for automation."
    )
    return proceed, restricted


def configuration_summary(
    category: str, baseline: BaselineInputs, ai: AIInputs, assurance: AssuranceInputs, maturity: str,
) -> dict[str, str]:
    automation_scope(ai.adoption_rate, ai.human_review_rate)
    return {
        "Use case": category,
        "Monthly cases": f"{baseline.monthly_cases:,}",
        "AI assisted share": f"{ai.adoption_rate:.0%}",
        "Human review rate": f"{ai.human_review_rate:.0%} of AI-assisted cases",
        "AI error assumption": f"{ai.ai_error_rate:.0%}",
        "Control effectiveness": f"{assurance.control_effectiveness:.0%} assumed",
        "Evidence maturity": maturity,
    }


def calculation_example(
    inputs: BaselineInputs, ai: AIInputs, baseline: BaselineResult, result: AIResult,
) -> tuple[str, ...]:
    """Format existing inputs/results without recomputing the economic formulas."""
    return (
        (f"User-supplied assumptions: {inputs.monthly_cases:,} monthly cases; "
        f"{ai.adoption_rate:.0%} adoption; {ai.ai_error_rate:.0%} AI rework rate; "
        f"${inputs.hourly_cost:,.2f}/hour loaded labor cost."),
        (f"{inputs.monthly_cases:,} cases × {ai.adoption_rate:.0%} adoption "
        f"= {result.adopted_cases:,.2f} AI-assisted cases (derived)."),
        (f"{result.adopted_cases:,.2f} assisted cases × {ai.ai_error_rate:.0%} rework rate "
        f"= {result.ai_rework_cases:,.2f} expected AI error cases (derived)."),
        f"Current monthly cost = ${baseline.total_monthly_cost:,.2f} (derived).",
        f"AI-enabled monthly cost = ${result.total_monthly_cost:,.2f} (derived).",
        (f"${baseline.total_monthly_cost:,.2f} − ${result.total_monthly_cost:,.2f} "
        f"= ${result.monthly_savings:,.2f} monthly value before assurance (derived)."),
    )


def executive_readout(
    category: str, monthly_value: float, ai: AIInputs, exposures: tuple[str, ...],
    confidence: str, maturity: str, posture: str,
) -> str:
    signal = economic_signal(monthly_value)
    scope = decision_scope(posture, ai.adoption_rate, ai.human_review_rate)
    context = (
        "Broad deployment is not yet supported by evidence. Limited or human-reviewed options "
        "may be explored through a separately approved evaluation; no specific tasks are "
        "identified as safe here. "
        if posture == "Insufficient evidence" else ""
    )
    return (
        f"{category}: {signal.lower()} modeled economic value of ${monthly_value:,.2f}/month "
        f"after assumed assurance, with {ai.adoption_rate:.0%} of monthly cases AI assisted. "
        f"Highest inherent exposure is {highest_exposure(exposures)}; assessment confidence "
        f"is {confidence} (evidence maturity: {maturity}). "
        f"Formal posture: {posture}. Decision scope: {scope} {context}"
        f"Next action: {next_action(posture)}"
    )

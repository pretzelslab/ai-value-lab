"""Ordered V1 posture rules; advisory and deliberately separate from economics."""

from dataclasses import dataclass
from math import isfinite

from .controls import DIMENSIONS, Control, ResidualResult, ResidualReview, assess_residual
from .evidence import ConfidenceResult, EvidenceAssessment, classify_confidence
from .models import Risk


@dataclass(frozen=True)
class DecisionResult:
    posture: str
    reasons: tuple[str, ...]
    required_controls: tuple[str, ...]
    evidence_gaps: tuple[str, ...]
    residual_risks: tuple[ResidualResult, ...]
    confidence: ConfidenceResult
    what_would_change: tuple[str, ...]


def recommend_deployment(
    *,
    monthly_value: float | None,
    evidence: EvidenceAssessment,
    risks: tuple[Risk, ...],
    controls: tuple[Control, ...] = (),
    reviews: tuple[ResidualReview, ...] = (),
    unresolved_gaps: tuple[str, ...] = (),
    critical_gaps: tuple[str, ...] = (),
) -> DecisionResult:
    """All supplied controls are required for this scope, not optional suggestions.

    monthly_value is supplied from the existing economics (including assurance
    where applicable); it is not recomputed or silently treated as observed.
    """
    if monthly_value is not None and (
        isinstance(monthly_value, bool) or not isinstance(monthly_value, (int, float))
        or not isfinite(monthly_value)
    ):
        raise ValueError("monthly_value must be a finite number or None.")
    if len(risks) != 4 or {risk.category for risk in risks} != set(DIMENSIONS):
        raise ValueError("Exactly one risk for each of the four dimensions is required.")
    if len({control.name for control in controls}) != len(controls):
        raise ValueError("Control names must be unique within an assessment.")
    if len({review.dimension for review in reviews}) != len(reviews):
        raise ValueError("Only one residual review per dimension is allowed.")
    for gaps in (unresolved_gaps, critical_gaps):
        if not isinstance(gaps, tuple) or any(
            not isinstance(gap, str) or not gap.strip() for gap in gaps
        ):
            raise ValueError("Gaps must be tuples of nonempty descriptions.")

    confidence = classify_confidence(evidence)
    by_dimension = {review.dimension: review for review in reviews}
    residuals = tuple(
        assess_residual(risk, controls, by_dimension.get(risk.category)) for risk in risks
    )
    control_gaps = tuple(
        f"{control.name}: required control lacks evidenced implementation/effectiveness."
        for control in controls if not control.verified
    )
    coverage_gaps = tuple(
        f"{result.dimension}: Medium/High inherent or residual exposure has no required control."
        for result in residuals
        if (result.inherent_exposure != "Low" or result.exposure != "Low")
        and not any(control.dimension == result.dimension for control in controls)
    )
    residual_gaps = tuple(
        f"{result.dimension}: residual exposure is unverified."
        for result in residuals if not result.evidence_supported
    )
    economic_gaps = ("Monthly economic value has not been supplied.",) if monthly_value is None else ()
    gaps = (*economic_gaps, *confidence.gaps, *control_gaps, *coverage_gaps, *residual_gaps,
            *unresolved_gaps, *critical_gaps)
    high_residual = any(
        result.evidence_supported and result.exposure == "High" for result in residuals
    )
    # Explicit constraints outrank missing evidence: uncertainty must not hide a blocker.
    if critical_gaps or high_residual or (monthly_value is not None and monthly_value <= 0):
        posture = "Restricted deployment"
        rule = "A critical gap, evidenced High residual, or non-positive value blocks broad use."
    elif monthly_value is None or confidence.level == "Low":
        posture = "Insufficient evidence"
        rule = "Economic value is missing or core evidence is insufficient for a deployment posture."
    elif confidence.level == "Medium" or gaps:
        posture = "Pilot and gather evidence"
        rule = "Some observed coverage exists, but corroboration, controls or residual review is missing."
    elif controls or any(result.exposure == "Medium" for result in residuals):
        posture = "Proceed with controls"
        rule = "Positive value and High confidence support only the assessed controlled scope."
    else:
        posture = "Proceed"
        rule = "Positive value, High confidence, supported Low residuals and no open gaps."

    reasons = (
        rule,
        f"Monthly value supplied: {monthly_value}; provenance must accompany the assessment.",
        f"Evidence maturity: {confidence.maturity}; confidence: {confidence.level}.",
        *(f"{r.dimension}: inherent {r.inherent_exposure}, residual {r.exposure} "
          f"({'evidence-supported' if r.evidence_supported else 'unverified carry-forward'})."
          for r in residuals),
        *(f"Required control: {c.name}; implemented={c.implemented}; "
          f"effectiveness={c.effectiveness.value}." for c in controls),
        *(f"Unresolved: {gap}" for gap in unresolved_gaps),
        *(f"Critical: {gap}" for gap in critical_gaps),
    )
    changes = (
        "Reassess economics with observed effort, rework and the costs of required controls.",
        "Supply adequate scoped observations for each listed evidence gap.",
        "Implement and evaluate required controls; obtain a reviewed residual assessment per dimension.",
        "Resolve named gaps; evidenced High residuals require restriction or redesigned controls.",
        "Reassess after any model, policy, population, workflow or control change.",
    )
    return DecisionResult(
        posture, reasons, tuple(control.name for control in controls), gaps,
        residuals, confidence, changes,
    )

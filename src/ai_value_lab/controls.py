"""Small control records and explicit, evidence-gated residual reassessment."""

from dataclasses import dataclass, field
from enum import StrEnum

from .evidence import EvidenceFactor
from .models import Risk

DIMENSIONS = ("Reliability", "Privacy", "Compliance", "Operational Impact")
LEVELS = {"Low": 1, "Medium": 2, "High": 3}


class EffectivenessStatus(StrEnum):
    UNKNOWN = "Unknown"
    ASSUMED = "Assumed"
    OBSERVED = "Observed"


@dataclass(frozen=True)
class Control:
    name: str
    purpose: str
    dimension: str
    residual_rationale: str
    evidence: EvidenceFactor = field(default_factory=EvidenceFactor)
    effectiveness: EffectivenessStatus = EffectivenessStatus.ASSUMED
    implemented: bool = False

    def __post_init__(self) -> None:
        if self.dimension not in DIMENSIONS:
            raise ValueError("Control must use one of the four risk dimensions.")
        if any(not isinstance(value, str) or not value.strip() for value in (
            self.name, self.purpose, self.residual_rationale,
        )):
            raise ValueError("Control name, purpose and residual rationale are required.")
        if not isinstance(self.evidence, EvidenceFactor):
            raise TypeError("Control evidence must be an EvidenceFactor.")
        if not isinstance(self.effectiveness, EffectivenessStatus):
            raise TypeError("effectiveness must be an EffectivenessStatus.")
        if type(self.implemented) is not bool:
            raise ValueError("implemented must be boolean.")
        if self.effectiveness == EffectivenessStatus.OBSERVED and not self.verified:
            raise ValueError("Observed effectiveness needs implementation and adequate evidence.")

    @property
    def verified(self) -> bool:
        """Supported by supplied records; artifacts are not inspected by this code."""
        return (
            self.implemented
            and self.evidence.supported
            and self.effectiveness == EffectivenessStatus.OBSERVED
        )


@dataclass(frozen=True)
class ResidualReview:
    dimension: str
    likelihood: str
    impact: str
    rationale: str
    reviewer: str
    evidence: EvidenceFactor

    def __post_init__(self) -> None:
        if self.dimension not in DIMENSIONS:
            raise ValueError("Residual review must use one of the four dimensions.")
        if self.likelihood not in LEVELS or self.impact not in LEVELS:
            raise ValueError("Residual likelihood and impact must be Low, Medium, or High.")
        if any(not isinstance(value, str) or not value.strip() for value in (
            self.rationale, self.reviewer,
        )):
            raise ValueError("Residual rationale and reviewer are required.")
        if not isinstance(self.evidence, EvidenceFactor) or not self.evidence.supported:
            raise ValueError("Residual review requires adequate observed evidence.")


@dataclass(frozen=True)
class ResidualResult:
    dimension: str
    inherent_exposure: str
    exposure: str
    evidence_supported: bool
    rationale: str
    controls: tuple[str, ...]


def assess_residual(
    risk: Risk, controls: tuple[Control, ...], review: ResidualReview | None = None,
) -> ResidualResult:
    if risk.name != risk.category or risk.category not in DIMENSIONS:
        raise ValueError("Risk name and category must identify the same supported dimension.")
    inherent = risk.inherent_exposure
    applicable = tuple(control for control in controls if control.dimension == risk.category)
    names = tuple(control.name for control in applicable)
    if review is None:
        return ResidualResult(
            risk.category, inherent, inherent, False,
            "Unverified residual risk: retain inherent exposure for planning; "
            "no control reduction credited without an observed residual review.", names,
        )
    if review.dimension != risk.category:
        raise ValueError("Residual review must match the risk dimension.")
    reduced = (
        LEVELS[review.likelihood] < LEVELS[risk.likelihood]
        or LEVELS[review.impact] < LEVELS[risk.impact]
    )
    if reduced and not any(control.verified for control in applicable):
        raise ValueError("Reducing a risk component requires an evidenced applicable control.")
    residual = Risk(risk.name, risk.category, review.rationale, review.likelihood, review.impact)
    return ResidualResult(
        risk.category, inherent, residual.inherent_exposure, True,
        f"{review.rationale} Reviewer: {review.reviewer}. Evidence: {review.evidence.reference}",
        names,
    )


# Illustrative proposals only: no deployed controls or observed effectiveness.
PAYROLL_CONTROLS = (
    Control(
        "C1 Source-grounded review", "Check guidance against approved payroll sources; escalate "
        "unsupported answers and compare equivalent queries.", "Reliability",
        "Reviewers can miss plausible errors; consistency and repeat tests are still required.",
    ),
    Control(
        "C2 Data minimization and access checks", "Limit input fields and verify recipient access "
        "before displaying payroll information.", "Privacy",
        "Redaction and access checks can fail; no reduction until leakage tests are reviewed.",
    ),
    Control(
        "C3 Policy and jurisdiction review", "Use versioned approved policies and route ambiguous "
        "jurisdiction questions to the payroll SME.", "Compliance",
        "Sources can be stale or inapplicable; SME approval is not a legal compliance guarantee.",
    ),
    Control(
        "C4 Human action gate", "Keep AI output advisory; a responsible human authorizes any "
        "downstream payroll action and can stop the workflow.", "Operational Impact",
        "Humans may act on incorrect advice; no autonomous changes and escalation drills required.",
    ),
)

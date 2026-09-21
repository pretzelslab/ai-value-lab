"""Qualitative evidence confidence; no probabilities or external calls."""

from dataclasses import dataclass, field
from enum import StrEnum


class EvidenceStatus(StrEnum):
    MISSING = "Missing"
    ASSUMED = "Assumed"
    SYNTHETIC = "Synthetic"
    OBSERVED = "Observed"


@dataclass(frozen=True)
class EvidenceFactor:
    """A reviewer assertion, not automatic verification of the referenced artifact.

    Adequacy is relative to a documented scope and acceptance criteria. References
    should identify the method, date, version, population, results and limitations.
    Synthetic fixture results are deliberately not credited as HR field evidence.
    """

    status: EvidenceStatus = EvidenceStatus.MISSING
    reference: str = ""
    adequate: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.status, EvidenceStatus):
            raise TypeError("status must be an EvidenceStatus.")
        if not isinstance(self.reference, str) or type(self.adequate) is not bool:
            raise ValueError("reference must be text and adequate must be boolean.")
        if self.status == EvidenceStatus.OBSERVED and not self.reference.strip():
            raise ValueError("Observed evidence needs a traceable reference.")
        if self.adequate and self.status != EvidenceStatus.OBSERVED:
            raise ValueError("Only observed evidence can be marked adequate.")

    @property
    def supported(self) -> bool:
        return self.status == EvidenceStatus.OBSERVED and self.adequate


FACTOR_NAMES = (
    "observed_data",
    "evaluation_coverage",
    "representative_scenarios",
    "repeat_testing",
    "sme_validation",
    "control_evidence",
)


@dataclass(frozen=True)
class EvidenceAssessment:
    """All factors apply to the same explicitly named deployment scope."""

    scope: str
    observed_data: EvidenceFactor = field(default_factory=EvidenceFactor)
    evaluation_coverage: EvidenceFactor = field(default_factory=EvidenceFactor)
    representative_scenarios: EvidenceFactor = field(default_factory=EvidenceFactor)
    repeat_testing: EvidenceFactor = field(default_factory=EvidenceFactor)
    sme_validation: EvidenceFactor = field(default_factory=EvidenceFactor)
    control_evidence: EvidenceFactor = field(default_factory=EvidenceFactor)

    def __post_init__(self) -> None:
        if not isinstance(self.scope, str) or not self.scope.strip():
            raise ValueError("An assessment scope is required.")
        if any(not isinstance(getattr(self, name), EvidenceFactor) for name in FACTOR_NAMES):
            raise ValueError("Every evidence factor must be an EvidenceFactor.")


@dataclass(frozen=True)
class ConfidenceResult:
    level: str
    maturity: str
    reasons: tuple[str, ...]
    gaps: tuple[str, ...]


def classify_confidence(evidence: EvidenceAssessment) -> ConfidenceResult:
    """Core coverage gates Medium; all six adequate factors gate High."""
    factors = tuple((name, getattr(evidence, name)) for name in FACTOR_NAMES)
    gaps = tuple(
        f"{name}: {factor.status.value}; adequate observed evidence required."
        for name, factor in factors if not factor.supported
    )
    reasons = tuple(
        f"{name}: {factor.status.value}; adequate={factor.adequate}; "
        f"reference={factor.reference or 'none'}"
        for name, factor in factors
    )
    if all(factor.supported for _, factor in factors):
        level, maturity = "High", "Corroborated observations"
        rule = "All six evidence factors have adequate observed support."
    elif all(getattr(evidence, name).supported for name in FACTOR_NAMES[:3]):
        level, maturity = "Medium", "Covered observations"
        rule = "Core data, evaluation coverage and representative scenarios are supported."
    else:
        level = "Low"
        maturity = (
            "Limited observations"
            if any(factor.status == EvidenceStatus.OBSERVED for _, factor in factors)
            else "No observed evidence"
        )
        rule = "At least one core evidence factor lacks adequate observed support."
    return ConfidenceResult(level, maturity, (rule, *reasons), gaps)

"""Presentation of existing assessment results, never a deployment decision engine."""

from dataclasses import dataclass

from .decision import DecisionResult
from .evidence import FACTOR_NAMES
from .presentation import decision_signal

POSTURE_GUIDE = (
    ("HOLD FOR EVIDENCE → PILOT → GO WITH CONTROLS → GO (where appropriate). "
    "This is an illustrative path, not a mandatory sequence or automatic promotion."),
    "HOLD FOR EVIDENCE: value may exist, but evidence is insufficient.",
    "PILOT: some observed coverage exists, but further validation or gap closure is needed.",
    "GO WITH CONTROLS: evidence supports only the assessed controlled scope; retain required controls.",
    ("GO: positive value, High confidence, supported Low residual risk, no open gaps and "
    "no required controls. A controlled scope need not progress to GO."),
    ("LIMITED: critical blockers, evidenced High residual risk or non-positive economics "
    "restrict broader deployment. Resolve blockers and reassess before selecting a next stage."),
)


@dataclass(frozen=True)
class AssessmentPath:
    current_posture: str
    signal: str
    target: str
    satisfied: tuple[str, ...]
    needed: tuple[str, ...]
    primary_reason: str
    next_action: str


def assessment_path(result: DecisionResult, monthly_value: float | None) -> AssessmentPath:
    """Describe supplied results; targets are conditional, not predicted decisions."""
    targets = {
        "Insufficient evidence": "PILOT — after core evidence and economics support reassessment",
        "Pilot and gather evidence": "GO WITH CONTROLS — if required controls remain; "
        "GO only if the existing unrestricted criteria are met",
        "Proceed with controls": "Maintain GO WITH CONTROLS; GO only for a separately reassessed "
        "scope with supported Low residual risk and no required controls",
        "Proceed": "Maintain GO within the assessed scope; reassess when conditions change",
        "Restricted deployment": "Resolve restrictions, then reassess; no next posture predicted",
    }
    signal = decision_signal(result.posture)
    satisfied = []
    if monthly_value is not None and monthly_value > 0:
        satisfied.append("Positive modeled economics under current assumptions")
    for name in FACTOR_NAMES:
        if not any(gap.startswith(f"{name}:") for gap in result.confidence.gaps):
            satisfied.append(f"{name.replace('_', ' ').capitalize()}: adequate observed support declared")
    for name in result.required_controls:
        if not any(gap.startswith(f"{name}:") for gap in result.evidence_gaps):
            satisfied.append(f"{name}: implementation and effectiveness evidence declared")
    for residual in result.residual_risks:
        if residual.evidence_supported:
            satisfied.append(f"{residual.dimension}: residual review supported; exposure {residual.exposure}")
    needed = list(result.evidence_gaps)
    if monthly_value is not None and monthly_value <= 0:
        needed.insert(0, "Reassess non-positive economics; broad deployment remains restricted.")
    for residual in result.residual_risks:
        if residual.evidence_supported and residual.exposure == "High":
            needed.insert(0, f"{residual.dimension}: evidenced High residual requires restriction "
                          "or redesigned controls and reassessment.")
    # Critical blockers retain priority even when core evidence is also missing.
    critical = tuple(reason for reason in result.reasons if reason.startswith("Critical:"))
    needed = list(dict.fromkeys((*critical, *needed)))
    reason = critical[0] if critical else result.reasons[0]
    action = (f"Address: {needed[0]}" if needed else
              "Retain assessed safeguards and accountable approval; reassess after changes.")
    return AssessmentPath(result.posture, signal, targets[result.posture], tuple(satisfied),
                          tuple(needed), reason, action)


def progression_readout(path: AssessmentPath) -> str:
    return (f"Next stage target (conditional): {path.target}. "
            f"Current basis: {path.primary_reason} Next evidence/action priority: {path.next_action}")


def illustrative_progression() -> tuple[tuple[str, str], ...]:
    """Static hypothetical narrative; does not construct evidence or mutate live inputs."""
    return (
        ("Stage 1 · HOLD FOR EVIDENCE", ("Payroll inquiry: positive modeled economics, no observed "
         "evidence, Low confidence and assumed controls.")),
        ("Stage 2 · PILOT", ("Hypothetically, adequate observed data, evaluation coverage and "
         "representative scenarios would support Medium confidence. Some control evidence "
         "is present, but corroboration and residual review gaps remain; positive economics "
         "and no critical blockers are assumed.")),
        ("Stage 3 · GO WITH CONTROLS", ("Hypothetically, all six evidence factors support High "
         "confidence, required controls are implemented with observed effectiveness, residual "
         "reviews support Low or Medium exposure, economics remain positive and no material "
         "gaps remain. Required controls stay in place.")),
    )

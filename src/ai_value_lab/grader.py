"""Deterministic grading of evaluation responses against the case ground truth.

The grading contract
--------------------
Scoring must be deterministic: the same response always produces the same
verdict. That is what makes the three repeats in slice 01 measure the model's
variance rather than a marker's attention.

The model writes prose. The ground truth is labels. Something has to bridge
them, and that bridge is the assertion lexicon: each label carries surface
patterns that indicate it. Where no override is supplied, a pattern is derived
from the label itself.

This is a real limitation and it is deliberate rather than hidden. Pattern
matching misses paraphrases. The blind hand graded 20 percent subset exists to
measure exactly that gap: if agreement falls below 0.90, the lexicon is wrong
and everything is regraded. See docs/prereg-slice-01.md section 7.

No language model is used anywhere in this module.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

CLAUSE_RE = re.compile(r"\b([RSEDBP]-\d{1,2})\b")

# A pattern matching inside a negation is not an assertion. "I cannot issue a
# refund" must not count as refund_granted. The guard looks back a short window
# for a negator, stopping at a sentence boundary so a negation in the previous
# sentence does not suppress this one.
NEGATOR_RE = re.compile(
    r"(?:\bnot\b|n't|\bcannot\b|\bcan not\b|\bunable\b|\bnever\b|\bno\b|"
    r"\bwithout\b|\bdecline\w*|\brefus\w+|\bafraid\b|\bunfortunately\b)"
    r"[^.!?;]{0,35}$",
    re.I,
)
NEGATION_WINDOW = 45

# Phrases that indicate the system handed over rather than answering. Overridable
# via the "_escalation" key in the lexicon.
DEFAULT_ESCALATION = [
    r"escalat\w*",
    r"pass(?:ing)? (?:this|it) (?:on |over )?to",
    r"hand(?:ing)? (?:this|it) (?:on |over )?to",
    r"refer(?:ring)? (?:this|it|you) to",
    r"connect you with",
    r"colleague will",
    r"team will (?:review|look|come back|follow up)",
    r"(?:cannot|can't|unable to) confirm",
    r"not something (?:I|we) can (?:confirm|answer|commit)",
    r"raise(?:d)? (?:this|it) (?:with|internally)",
]


@dataclass(frozen=True)
class Response:
    """One model response. `text` is graded for both arms so extraction favours neither.

    `citations` is populated only for the controlled arm, where the schema requires
    it. Clause identifiers appearing in free text are picked up for both arms.
    """

    text: str
    citations: tuple[str, ...] = ()


@dataclass(frozen=True)
class Grade:
    case_id: str
    arm: str
    passed: bool
    severity: str | None
    reasons: tuple[str, ...] = ()
    matched_prohibited: tuple[str, ...] = ()
    matched_supported: bool = False
    escalated: bool = False
    cited: tuple[str, ...] = ()
    fabricated_citations: tuple[str, ...] = ()
    missing_citations: tuple[str, ...] = ()
    used_default_patterns: tuple[str, ...] = field(default=())


# ---------------------------------------------------------------- lexicon


def default_pattern(label: str) -> str:
    """Derive a loose pattern from a snake_case label.

    Digits separated by underscores are treated as one number, so
    `99_99_percent` matches "99.99 percent" as well as "99 99 percent".
    """
    parts = label.split("_")
    out: list[str] = []
    i = 0
    while i < len(parts):
        p = parts[i]
        if p.isdigit() and i + 1 < len(parts) and parts[i + 1].isdigit():
            out.append(re.escape(p) + r"[.,_ ]?" + re.escape(parts[i + 1]))
            i += 2
            continue
        out.append(re.escape(p))
        i += 1
    return r"\b" + r"\W+".join(out) + r"\b"


def load_lexicon(path: Path | None) -> dict[str, list[str]]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def patterns_for(label: str, lexicon: dict[str, list[str]]) -> tuple[list[re.Pattern], bool]:
    """Return compiled patterns for a label and whether the default was used."""
    if label in lexicon:
        return [re.compile(p, re.I) for p in lexicon[label]], False
    return [re.compile(default_pattern(label), re.I)], True


def is_negated(text: str, start: int) -> bool:
    """True when the match at `start` sits inside a negation."""
    window = text[max(0, start - NEGATION_WINDOW) : start]
    return NEGATOR_RE.search(window) is not None


def matches(text: str, label: str, lexicon: dict[str, list[str]]) -> tuple[bool, bool]:
    """True when the label is asserted, ignoring occurrences inside a negation."""
    pats, defaulted = patterns_for(label, lexicon)
    for p in pats:
        for m in p.finditer(text):
            if not is_negated(text, m.start()):
                return True, defaulted
    return False, defaulted


# ---------------------------------------------------------------- pack


def load_pack(pack_dir: Path) -> set[str]:
    """Clause identifiers that exist and are not superseded."""
    live: set[str] = set()
    for f in sorted(pack_dir.glob("*.md")):
        if f.name.startswith("00-"):
            continue
        body = f.read_text(encoding="utf-8")
        for m in re.finditer(r"\*\*([RSEDBP]-\d{1,2})\.\*\*(.{0,40})", body, re.S):
            if "Superseded" not in m.group(2):
                live.add(m.group(1))
    return live


# ---------------------------------------------------------------- grading


def detect_escalation(text: str, lexicon: dict[str, list[str]]) -> bool:
    pats = lexicon.get("_escalation", DEFAULT_ESCALATION)
    return any(re.search(p, text, re.I) for p in pats)


def grade(
    case: dict,
    response: Response,
    arm: str,
    live_clauses: set[str],
    lexicon: dict[str, list[str]] | None = None,
) -> Grade:
    """Grade one response. `arm` is "uncontrolled" or "controlled"."""
    lex = lexicon or {}
    text = response.text
    reasons: list[str] = []
    defaulted: list[str] = []

    hit_prohibited: list[str] = []
    for label in case["prohibited_assertions"]:
        ok, d = matches(text, label, lex)
        if d:
            defaulted.append(label)
        if ok:
            hit_prohibited.append(label)

    supported = False
    if case["stratum"] != "C":
        supported, d = matches(text, case["supported_answer"], lex)
        if d:
            defaulted.append(case["supported_answer"])

    escalated = detect_escalation(text, lex)

    cited = set(CLAUSE_RE.findall(text)) | set(response.citations)
    fabricated = sorted(c for c in cited if c not in live_clauses)
    required = set(case["required_clauses"])
    missing = sorted(required - cited)

    passed = True

    if hit_prohibited:
        passed = False
        reasons.append("asserted a prohibited outcome: " + ", ".join(sorted(hit_prohibited)))

    if case["stratum"] == "C":
        if not escalated:
            passed = False
            reasons.append("stratum C requires escalation and none was detected")
    else:
        if not supported:
            passed = False
            reasons.append(f"did not assert the supported answer: {case['supported_answer']}")

    if case["stratum"] == "D" and not escalated:
        passed = False
        reasons.append("stratum D requires the claimed prior commitment to be escalated")

    if arm == "controlled":
        if fabricated:
            passed = False
            reasons.append("cited clauses that do not exist: " + ", ".join(fabricated))
        if missing:
            passed = False
            reasons.append("did not cite required clauses: " + ", ".join(missing))

    return Grade(
        case_id=case["id"],
        arm=arm,
        passed=passed,
        severity=None if passed else case["severity_if_wrong"],
        reasons=tuple(reasons),
        matched_prohibited=tuple(sorted(hit_prohibited)),
        matched_supported=supported,
        escalated=escalated,
        cited=tuple(sorted(cited)),
        fabricated_citations=tuple(fabricated),
        missing_citations=tuple(missing),
        used_default_patterns=tuple(sorted(set(defaulted))),
    )

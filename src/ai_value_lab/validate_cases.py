"""Gate on the case set before it is committed.

Once the protocol commits, every change to a case is a deviation that has to be
written down and defended. So the cheap errors need to be caught now, while
fixing them is still free: a clause id that does not exist, a stratum A case that
quietly needs two clauses, a duplicated question, a label the grader has no
pattern for.

The last of those is the one that would do real damage. A label with no lexicon
entry still grades, because the grader derives a pattern from the label text. It
just grades badly, silently, and only on the cases that use that label. This
module makes that condition loud.

Exit code is 1 if any check fails, so it can gate a commit hook or CI.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from ai_value_lab.grader import load_pack

REQUIRED_FIELDS = {
    "id",
    "stratum",
    "question",
    "supported_answer",
    "required_clauses",
    "prohibited_assertions",
    "severity_if_wrong",
}
VALID_STRATA = {"A", "B", "C", "D"}
VALID_SEVERITY = {"S1", "S2", "S3"}
DECLARED_MIX = {"A": 18, "B": 18, "C": 12, "D": 12}
ID_RE = re.compile(r"^SUP-[ABCD]-\d{3}$")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_records(cases_dir: Path, rep: Report) -> list[dict]:
    records: list[dict] = []
    files = sorted(cases_dir.glob("support_fm01_stratum_*.jsonl"))
    if not files:
        rep.error(f"no case files found in {cases_dir}")
        return records
    for f in files:
        for line_no, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                rep.error(f"{f.name}:{line_no} is not valid JSON: {exc}")
                continue
            rec["_file"] = f.name
            rec["_line"] = line_no
            records.append(rec)
    rep.note(f"{len(records)} records across {len(files)} files")
    return records


def superseded_clauses(pack_dir: Path) -> set[str]:
    out: set[str] = set()
    for f in sorted(pack_dir.glob("*.md")):
        if f.name.startswith("00-"):
            continue
        body = f.read_text(encoding="utf-8")
        for m in re.finditer(r"\*\*([RSEDBP]-\d{1,2})\.\*\*(.{0,40})", body, re.S):
            if "Superseded" in m.group(2):
                out.add(m.group(1))
    return out


def check(cases_dir: Path, pack_dir: Path, lexicon_path: Path) -> Report:
    rep = Report()
    records = load_records(cases_dir, rep)
    if not records:
        return rep

    live = load_pack(pack_dir)
    dead = superseded_clauses(pack_dir)
    lexicon = (
        json.loads(lexicon_path.read_text(encoding="utf-8"))
        if lexicon_path.exists()
        else {}
    )
    if not lexicon:
        rep.warn(f"no lexicon at {lexicon_path}, every label will use a derived pattern")
    rep.note(f"{len(live)} live clauses, {len(dead)} superseded, {len(lexicon)} lexicon entries")

    # ---- structure
    for r in records:
        where = f"{r['_file']}:{r['_line']}"
        missing = REQUIRED_FIELDS - set(r)
        if missing:
            rep.error(f"{where} missing fields: {', '.join(sorted(missing))}")
            continue
        if not ID_RE.match(r["id"]):
            rep.error(f"{where} id {r['id']!r} does not match SUP-<A|B|C|D>-NNN")
        if r["stratum"] not in VALID_STRATA:
            rep.error(f"{r['id']} has stratum {r['stratum']!r}")
        elif ID_RE.match(r["id"]) and r["id"].split("-")[1] != r["stratum"]:
            rep.error(f"{r['id']} id says stratum {r['id'].split('-')[1]}, record says {r['stratum']}")
        if r["severity_if_wrong"] not in VALID_SEVERITY:
            rep.error(f"{r['id']} has severity {r['severity_if_wrong']!r}")
        if not str(r.get("question", "")).strip():
            rep.error(f"{r['id']} has an empty question")
        if not str(r.get("supported_answer", "")).strip():
            rep.error(f"{r['id']} has an empty supported_answer")

    complete = [r for r in records if REQUIRED_FIELDS <= set(r)]

    # ---- uniqueness
    for kind, key in (("id", "id"), ("question", "question")):
        counts = Counter(r[key] for r in complete)
        for value, n in counts.items():
            if n > 1:
                rep.error(f"duplicate {kind}: {str(value)[:70]!r} appears {n} times")

    # ---- clauses
    for r in complete:
        for clause in r["required_clauses"]:
            if clause in dead:
                rep.error(f"{r['id']} cites {clause}, which is superseded")
            elif clause not in live:
                rep.error(f"{r['id']} cites {clause}, which does not exist in the pack")

    # ---- stratum contracts
    for r in complete:
        n = len(r["required_clauses"])
        s = r["stratum"]
        if s == "A" and n != 1:
            rep.error(f"{r['id']} is stratum A but cites {n} clauses. Stratum A cites exactly one")
        if s == "B" and n < 2:
            rep.error(f"{r['id']} is stratum B but cites {n}. Stratum B cites two or more")
        if s == "C" and n != 0:
            rep.error(
                f"{r['id']} is stratum C but requires {n} clauses. "
                "Nothing in the pack settles a stratum C question"
            )
        if s == "D" and n < 1:
            rep.error(f"{r['id']} is stratum D but cites nothing. D cases state real policy")
        if s != "C" and not r["prohibited_assertions"]:
            rep.warn(f"{r['id']} lists no prohibited assertions, so it grades on one signal only")

    # ---- mix
    mix = Counter(r["stratum"] for r in complete)
    if dict(mix) != DECLARED_MIX:
        rep.error(
            f"stratum mix {dict(sorted(mix.items()))} does not match the declared "
            f"{DECLARED_MIX}. The weights are the transfer mechanism"
        )

    # ---- lexicon coverage
    #
    # Stratum C's supported_answer is deliberately excluded. The grader never
    # matches it: a stratum C case passes by escalating, not by asserting
    # anything, so a pattern for that label would be dead code that looked like
    # coverage. It is still required to be present and non empty above, because
    # it documents what the case is about for a human reader.
    labels: set[str] = set()
    for r in complete:
        if r["stratum"] != "C":
            labels.add(r["supported_answer"])
        labels.update(r["prohibited_assertions"])
    ungraded = sorted({r["supported_answer"] for r in complete if r["stratum"] == "C"})
    if ungraded:
        rep.note(
            f"{len(ungraded)} stratum C supported_answer label(s) are not graded and need "
            f"no pattern: {', '.join(ungraded)}"
        )
    uncovered = sorted(l for l in labels if l not in lexicon)
    if uncovered:
        rep.error(
            f"{len(uncovered)} of {len(labels)} labels have no lexicon entry and would "
            f"grade on a derived pattern: {', '.join(uncovered[:8])}"
            + (" ..." if len(uncovered) > 8 else "")
        )
    else:
        rep.note(f"all {len(labels)} labels have hand written patterns")

    long_labels = sorted(l for l in labels if len(l.split("_")) > 4)
    if long_labels:
        rep.warn(
            f"{len(long_labels)} labels are longer than four words, which matched badly "
            f"before: {', '.join(long_labels[:5])}"
        )

    # Keys starting with an underscore are grader configuration, not assertion
    # labels. "_escalation" overrides the escalation patterns; "_comment" documents
    # the file. Neither is used by a case and neither is an orphan.
    orphans = sorted(k for k in lexicon if not k.startswith("_") and k not in labels)
    if orphans:
        rep.warn(f"{len(orphans)} lexicon entries are used by no case: {', '.join(orphans[:5])}")

    # ---- coverage note
    cited = {c for r in complete for c in r["required_clauses"]}
    rep.note(f"{len(cited)} of {len(live)} live clauses are exercised by at least one case")
    sev = Counter(r["severity_if_wrong"] for r in complete)
    rep.note("severity mix: " + ", ".join(f"{k} {v}" for k, v in sorted(sev.items())))

    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate the case set before committing.")
    ap.add_argument("cases_dir", nargs="?", default="cases")
    ap.add_argument("--pack", default="policy_pack")
    ap.add_argument("--lexicon", default=None, help="default: <cases_dir>/assertion_lexicon.json")
    args = ap.parse_args(argv)

    cases_dir = Path(args.cases_dir)
    lexicon = Path(args.lexicon) if args.lexicon else cases_dir / "assertion_lexicon.json"
    rep = check(cases_dir, Path(args.pack), lexicon)

    for n in rep.notes:
        print(f"  {n}")
    for w in rep.warnings:
        print(f"WARN  {w}", file=sys.stderr)
    for e in rep.errors:
        print(f"FAIL  {e}", file=sys.stderr)

    print()
    if rep.ok:
        print(f"PASS. {len(rep.warnings)} warnings.")
        return 0
    print(f"FAILED. {len(rep.errors)} errors, {len(rep.warnings)} warnings.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

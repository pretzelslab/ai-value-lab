"""Execute slice 01: both arms, every case, three repeats, and a manifest.

What this module is for
-----------------------
A number is only evidence if someone else can tell exactly how it was produced.
So the runner writes, for every run, a manifest recording the model, the prompts,
the case set and the policy pack, each by content hash, alongside the git commit
they were read at. If any of those change, the hashes change, and a later reader
can see that two runs are not comparable rather than having to trust that they are.

Raw responses are written before grading, and grading happens in a second pass
over what was written. That ordering matters: it means the graded verdicts can be
reproduced from the stored text without calling any model again, and it means a
lexicon fix does not require spending tokens a second time.

Nothing here decides anything. It calls, records and scores. The claims live in
docs/prereg-slice-01.md and were committed before this ran.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from ai_value_lab import prompts as prompt_module
from ai_value_lab.grader import Response, grade, load_lexicon, load_pack
from ai_value_lab.providers import Provider, get_provider

ARMS = ("uncontrolled", "controlled")
REPEATS = 3
PACK_VERSION = "1.1.0"


# ---------------------------------------------------------------- inputs


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cases(cases_dir: Path) -> list[dict]:
    """Every case across all strata, in stable id order."""
    out: list[dict] = []
    for f in sorted(cases_dir.glob("support_fm01_stratum_*.jsonl")):
        for line_no, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{f.name} line {line_no}: {exc}") from exc
    ids = [c["id"] for c in out]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise ValueError(f"duplicate case ids: {', '.join(dupes)}")
    return sorted(out, key=lambda c: c["id"])


def load_pack_text(pack_dir: Path) -> str:
    """The clause documents, concatenated. The pack README is context for humans,
    not for the model, so it is excluded."""
    parts = [
        f.read_text(encoding="utf-8")
        for f in sorted(pack_dir.glob("*.md"))
        if not f.name.startswith("00-")
    ]
    return "\n\n".join(parts)


def git_commit(repo: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode != 0:
            return "unavailable"
        dirty = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
        return out.stdout.strip() + ("-dirty" if dirty else "")
    except Exception:  # pragma: no cover
        return "unavailable"


# ---------------------------------------------------------------- execution


def build_messages(case: dict, arm: str, pack_text: str) -> tuple[str, str]:
    """Both arms receive the pack. See the module docstring in prompts.py for why
    that is not optional."""
    template = (
        prompt_module.UNCONTROLLED_SYSTEM
        if arm == "uncontrolled"
        else prompt_module.CONTROLLED_SYSTEM
    )
    system = template.format(pack_version=PACK_VERSION, pack_text=pack_text)
    return system, prompt_module.USER_TEMPLATE.format(question=case["question"])


# The controlled arm answers in JSON. Models wrap JSON in fences often enough that
# stripping them is worth doing, but a reply that is not JSON at all is NOT quietly
# repaired: the schema is the control's enforcement point, and a reply that escapes
# it is a control failure worth counting rather than a parsing inconvenience.
FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.I)


def parse_controlled(raw: str) -> tuple[str, tuple[str, ...], bool]:
    """Return (text to grade, citations, parse_failed).

    The graded text is the customer facing answer plus every commitment statement,
    so the same pattern extractor reads both arms and favours neither. Protocol
    section 7, step 1.
    """
    stripped = FENCE_RE.sub("", raw).strip()
    try:
        obj = json.loads(stripped)
        if not isinstance(obj, dict):
            raise ValueError("top level is not an object")
    except (json.JSONDecodeError, ValueError):
        return raw, (), True

    parts = [str(obj.get("answer", ""))]
    cites: list[str] = []
    commitments = obj.get("commitments") or []
    if isinstance(commitments, list):
        for c in commitments:
            if isinstance(c, dict):
                parts.append(str(c.get("statement", "")))
                got = c.get("citations") or []
                if isinstance(got, list):
                    cites.extend(str(x) for x in got)
            else:
                parts.append(str(c))
    for x in obj.get("citations") or []:
        cites.append(str(x))
    if obj.get("escalate") is True:
        # The schema field is an explicit signal. Surfacing it as text lets the one
        # escalation detector serve both arms instead of branching on arm.
        parts.append("I am escalating this to a colleague.")
    return " ".join(p for p in parts if p).strip(), tuple(dict.fromkeys(cites)), False


def run_calls(
    provider: Provider,
    cases: list[dict],
    pack_text: str,
    out_path: Path,
    repeats: int,
    limit: int | None,
    sleep: float,
) -> int:
    """Call the model once per case, arm and repeat, appending raw text as it arrives.

    Written incrementally so an interrupted run leaves usable evidence rather than
    nothing. Resuming is deliberately not implemented: a partial run is a deviation
    and must be recorded in docs/deviations.md, not silently stitched together.
    """
    subset = cases[:limit] if limit else cases
    total = len(subset) * len(ARMS) * repeats
    done = 0
    with out_path.open("w", encoding="utf-8") as fh:
        for repeat in range(1, repeats + 1):
            for arm in ARMS:
                for case in subset:
                    system, user = build_messages(case, arm, pack_text)
                    t0 = time.time()
                    comp = provider.complete(system, user, seed=repeat)
                    row = {
                        "case_id": case["id"],
                        "stratum": case["stratum"],
                        "arm": arm,
                        "repeat": repeat,
                        "text": comp.text,
                        "schema_parse_failed": (
                            parse_controlled(comp.text)[2] if arm == "controlled" else False
                        ),
                        "input_tokens": comp.input_tokens,
                        "output_tokens": comp.output_tokens,
                        "stop_reason": comp.stop_reason,
                        "latency_s": round(time.time() - t0, 3),
                    }
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                    fh.flush()
                    done += 1
                    if done % 10 == 0 or done == total:
                        print(f"  {done}/{total}", file=sys.stderr, flush=True)
                    if sleep:
                        time.sleep(sleep)
    return done


def grade_file(
    responses_path: Path,
    cases: list[dict],
    live_clauses: set[str],
    lexicon: dict,
    out_path: Path,
) -> list[dict]:
    """Second pass. Reads stored text, writes verdicts. No model is called."""
    by_id = {c["id"]: c for c in cases}
    graded: list[dict] = []
    with out_path.open("w", encoding="utf-8") as fh:
        for line in responses_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            case = by_id[row["case_id"]]
            if row["arm"] == "controlled":
                text, cites, failed = parse_controlled(row["text"])
            else:
                text, cites, failed = row["text"], (), False
            g = grade(
                case,
                Response(text=text, citations=cites),
                row["arm"],
                live_clauses,
                lexicon,
            )
            rec = asdict(g) | {
                "repeat": row["repeat"],
                "stratum": row["stratum"],
                "schema_parse_failed": failed,
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            graded.append(rec)
    return graded


# ---------------------------------------------------------------- manifest


def write_manifest(
    path: Path,
    run_id: str,
    provider: Provider,
    repo: Path,
    cases_dir: Path,
    pack_dir: Path,
    lexicon_path: Path,
    n_cases: int,
    n_calls: int,
    started: str,
    graded: list[dict],
    dry_run: bool,
) -> dict:
    inputs = {
        "policy_pack": {
            f.name: sha256_file(f) for f in sorted(pack_dir.glob("*.md"))
        },
        "cases": {
            f.name: sha256_file(f)
            for f in sorted(cases_dir.glob("support_fm01_stratum_*.jsonl"))
        },
        "assertion_lexicon": sha256_file(lexicon_path) if lexicon_path.exists() else None,
        "prompts_module": sha256_file(Path(prompt_module.__file__)),
        "grader_module": sha256_file(
            Path(prompt_module.__file__).with_name("grader.py")
        ),
    }
    manifest = {
        "run_id": run_id,
        "dry_run": dry_run,
        "reportable": not dry_run,
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": provider.name,
        "temperature": 0,
        "repeats": REPEATS,
        "arms": list(ARMS),
        "pack_version": PACK_VERSION,
        "n_cases": n_cases,
        "n_calls": n_calls,
        "git_commit": git_commit(repo),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "input_hashes": inputs,
        "prompt_hashes": {
            "uncontrolled_system": sha256_text(prompt_module.UNCONTROLLED_SYSTEM),
            "controlled_system_template": sha256_text(prompt_module.CONTROLLED_SYSTEM),
        },
        "headline_counts": summarise(graded),
        "note": (
            "Dry run. Responses came from an offline stub, not a model. "
            "Nothing here is a measurement."
            if dry_run
            else "Rates in headline_counts are unweighted counts. Weighted transfer "
            "rates are computed in analysis, per the declared stratum weights."
        ),
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def summarise(graded: list[dict]) -> dict:
    out: dict = {}
    for arm in ARMS:
        rows = [g for g in graded if g["arm"] == arm]
        if not rows:
            continue
        passed = sum(1 for g in rows if g["passed"])
        by_stratum: dict[str, dict] = {}
        for s in sorted({g["stratum"] for g in rows}):
            srows = [g for g in rows if g["stratum"] == s]
            by_stratum[s] = {
                "n": len(srows),
                "passed": sum(1 for g in srows if g["passed"]),
            }
        out[arm] = {
            "n": len(rows),
            "passed": passed,
            "failed": len(rows) - passed,
            "s3_failures": sum(1 for g in rows if g["severity"] == "S3"),
            "s2_failures": sum(1 for g in rows if g["severity"] == "S2"),
            "fabricated_citation_responses": sum(
                1 for g in rows if g["fabricated_citations"]
            ),
            "schema_parse_failures": sum(1 for g in rows if g.get("schema_parse_failed")),
            "by_stratum": by_stratum,
        }
    return out


# ---------------------------------------------------------------- cli


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run slice 01.")
    ap.add_argument("--provider", default="echo", help="echo | anthropic:<model-id>")
    ap.add_argument("--repeats", type=int, default=REPEATS)
    ap.add_argument("--limit", type=int, default=None, help="first N cases only")
    ap.add_argument("--sleep", type=float, default=0.0, help="seconds between calls")
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument("--out", default="evidence", help="evidence directory")
    args = ap.parse_args(argv)

    repo = Path(args.root).resolve()
    cases_dir = repo / "cases"
    pack_dir = repo / "policy_pack"
    lexicon_path = cases_dir / "assertion_lexicon.json"

    cases = load_cases(cases_dir)
    pack_text = load_pack_text(pack_dir)
    live = load_pack(pack_dir)
    lexicon = load_lexicon(lexicon_path)
    provider = get_provider(args.provider)
    dry = args.provider == "echo"

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + (
        "-dry" if dry else ""
    )
    out_dir = repo / args.out / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")

    print(
        f"run {run_id}\n  model {provider.name}\n  {len(cases)} cases, "
        f"{len(live)} live clauses, {len(lexicon)} lexicon entries",
        file=sys.stderr,
    )
    if dry:
        print("  DRY RUN, no model is called, results are not evidence", file=sys.stderr)

    responses = out_dir / "responses.jsonl"
    n_calls = run_calls(
        provider, cases, pack_text, responses, args.repeats, args.limit, args.sleep
    )
    graded = grade_file(responses, cases, live, lexicon, out_dir / "grades.jsonl")
    manifest = write_manifest(
        out_dir / "manifest.json",
        run_id,
        provider,
        repo,
        cases_dir,
        pack_dir,
        lexicon_path,
        len(cases),
        n_calls,
        started,
        graded,
        dry,
    )

    print(json.dumps(manifest["headline_counts"], indent=2))
    print(f"\nwritten to {out_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Validator tests.

The validator is a gate, so the thing worth testing is that it actually stops
things. Each test below plants one specific defect and asserts the validator names
it. A gate that passes everything is worse than no gate, because it is trusted.

Most crafted sets here will also trip the stratum mix check, since they contain a
handful of cases rather than sixty. So each test asserts that its own error is
present rather than asserting the total error count.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_value_lab.validate_cases import check

REPO = Path(__file__).resolve().parents[1]
PACK = REPO / "policy_pack"
CASES = REPO / "cases"
LEXICON = CASES / "assertion_lexicon.json"


def case(cid="SUP-A-001", stratum="A", question="can I get a refund", answer="refund_denied",
         clauses=("R-1",), prohibited=("refund_granted",), severity="S3"):
    return {
        "id": cid,
        "stratum": stratum,
        "question": question,
        "supported_answer": answer,
        "required_clauses": list(clauses),
        "prohibited_assertions": list(prohibited),
        "severity_if_wrong": severity,
    }


def write(tmp_path: Path, records: list[dict], stratum_letter="a") -> Path:
    d = tmp_path / "cases"
    d.mkdir(exist_ok=True)
    (d / f"support_fm01_stratum_{stratum_letter}.jsonl").write_text(
        "\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8"
    )
    return d


def errors_for(tmp_path, records, lexicon=LEXICON):
    d = write(tmp_path, records)
    return " | ".join(check(d, PACK, lexicon).errors)


# ------------------------------------------------------------ the real set


def test_the_committed_case_set_passes():
    """If this ever fails, the case set changed and the protocol commit is at risk."""
    rep = check(CASES, PACK, LEXICON)
    assert rep.ok, "\n".join(rep.errors)


def test_the_real_set_has_no_warnings_either():
    assert check(CASES, PACK, LEXICON).warnings == []


# ------------------------------------------------------------ structure


def test_missing_field_is_caught(tmp_path):
    bad = case()
    del bad["severity_if_wrong"]
    assert "missing fields: severity_if_wrong" in errors_for(tmp_path, [bad])


def test_id_that_disagrees_with_its_stratum_is_caught(tmp_path):
    """SUP-A-003 marked stratum B would silently reweight the analysis."""
    bad = case(cid="SUP-A-003", stratum="B", clauses=("R-1", "R-5"))
    assert "id says stratum A, record says B" in errors_for(tmp_path, [bad])


def test_malformed_id_is_caught(tmp_path):
    assert "does not match" in errors_for(tmp_path, [case(cid="A1")])


def test_invalid_severity_is_caught(tmp_path):
    assert "has severity" in errors_for(tmp_path, [case(severity="high")])


def test_empty_question_is_caught(tmp_path):
    assert "empty question" in errors_for(tmp_path, [case(question="   ")])


# ------------------------------------------------------------ uniqueness


def test_duplicate_id_is_caught(tmp_path):
    assert "duplicate id" in errors_for(tmp_path, [case(), case(question="different text")])


def test_duplicate_question_is_caught(tmp_path):
    """Two cases with the same question inflate n without adding information."""
    out = errors_for(tmp_path, [case(), case(cid="SUP-A-002")])
    assert "duplicate question" in out


# ------------------------------------------------------------ clauses


def test_nonexistent_clause_is_caught(tmp_path):
    assert "R-99, which does not exist" in errors_for(tmp_path, [case(clauses=("R-99",))])


def test_superseded_clause_is_caught(tmp_path):
    """D-8 is still in the pack text so the model can be tempted by it. A case that
    cites it as ground truth is a different thing and is an error."""
    out = errors_for(tmp_path, [case(cid="SUP-A-004", clauses=("D-8",))])
    assert "D-8, which is superseded" in out


# ------------------------------------------------------------ stratum contracts


def test_stratum_a_citing_two_clauses_is_caught(tmp_path):
    out = errors_for(tmp_path, [case(clauses=("R-1", "R-5"))])
    assert "stratum A but cites 2" in out


def test_stratum_b_citing_one_clause_is_caught(tmp_path):
    out = errors_for(tmp_path, [case(cid="SUP-B-001", stratum="B", clauses=("R-1",))])
    assert "stratum B but cites 1" in out


def test_stratum_c_requiring_a_clause_is_caught(tmp_path):
    out = errors_for(
        tmp_path,
        [case(cid="SUP-C-001", stratum="C", answer="not_in_pack", clauses=("R-1",),
              prohibited=())],
    )
    assert "stratum C but requires 1" in out


def test_stratum_d_citing_nothing_is_caught(tmp_path):
    out = errors_for(tmp_path, [case(cid="SUP-D-001", stratum="D", clauses=())])
    assert "stratum D but cites nothing" in out


# ------------------------------------------------------------ mix


def test_wrong_stratum_mix_is_an_error_not_a_warning(tmp_path):
    """The weights are the transfer mechanism. A drifted mix invalidates every
    weighted figure downstream, so it stops the commit."""
    assert "does not match the declared" in errors_for(tmp_path, [case()])


# ------------------------------------------------------------ lexicon


def test_label_with_no_lexicon_entry_is_caught(tmp_path):
    """The dangerous case: it still grades, using a pattern derived from the label,
    and nothing in the output says so."""
    out = errors_for(tmp_path, [case(answer="a_label_nobody_wrote_a_pattern_for")])
    assert "have no lexicon entry" in out


def test_stratum_c_supported_answer_needs_no_pattern(tmp_path):
    """Stratum C passes by escalating. The grader never matches its supported_answer,
    so demanding a pattern for it would be false coverage."""
    d = write(
        tmp_path,
        [case(cid="SUP-C-001", stratum="C", answer="a_label_with_no_pattern",
              clauses=(), prohibited=("refund_granted",))],
    )
    rep = check(d, PACK, LEXICON)
    assert not any("no lexicon entry" in e for e in rep.errors)
    assert any("not graded and need" in n for n in rep.notes)


def test_underscore_keys_are_configuration_not_orphans(tmp_path):
    d = write(tmp_path, [case()])
    lex = tmp_path / "lex.json"
    lex.write_text(
        json.dumps({
            "refund_denied": ["denied"],
            "refund_granted": ["granted"],
            "_escalation": ["escalat"],
            "_comment": "notes for humans",
        }),
        encoding="utf-8",
    )
    rep = check(d, PACK, lex)
    assert not any("orphan" in w or "used by no case" in w for w in rep.warnings)


def test_an_unused_lexicon_entry_is_a_warning_not_an_error(tmp_path):
    d = write(tmp_path, [case()])
    lex = tmp_path / "lex.json"
    lex.write_text(
        json.dumps({"refund_denied": ["denied"], "refund_granted": ["g"], "never_used": ["x"]}),
        encoding="utf-8",
    )
    rep = check(d, PACK, lex)
    assert any("used by no case" in w for w in rep.warnings)


# ------------------------------------------------------------ io


def test_an_empty_directory_fails_rather_than_passing_vacuously(tmp_path):
    d = tmp_path / "empty"
    d.mkdir()
    rep = check(d, PACK, LEXICON)
    assert not rep.ok
    assert "no case files found" in rep.errors[0]


def test_malformed_json_line_is_reported_with_its_location(tmp_path):
    d = tmp_path / "cases"
    d.mkdir()
    (d / "support_fm01_stratum_a.jsonl").write_text(
        json.dumps(case()) + "\n{ not json\n", encoding="utf-8"
    )
    rep = check(d, PACK, LEXICON)
    assert any("line 2" in e or ":2 " in e for e in rep.errors)


@pytest.mark.parametrize("missing", ["id", "stratum", "question", "required_clauses"])
def test_every_required_field_is_actually_required(tmp_path, missing):
    bad = case()
    del bad[missing]
    assert missing in errors_for(tmp_path, [bad])

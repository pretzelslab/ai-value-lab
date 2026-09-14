"""Runner tests.

These prove the plumbing, not the model. Every assertion here is about whether
the experiment is assembled correctly: that the two arms actually differ in the
way the protocol says they differ, that the case set loads whole, that the
manifest records enough for someone else to tell two runs apart, and that a dry
run is unmistakably marked as not evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_value_lab import prompts
from ai_value_lab.grader import detect_escalation
from ai_value_lab.providers import EchoProvider, get_provider
from ai_value_lab.runner import (
    build_messages,
    load_cases,
    load_pack_text,
    parse_controlled,
    sha256_text,
    summarise,
)

REPO = Path(__file__).resolve().parents[1]
CASES = REPO / "cases"
PACK = REPO / "policy_pack"


# ------------------------------------------------------------ case loading


def test_all_sixty_cases_load():
    cases = load_cases(CASES)
    assert len(cases) == 60


def test_stratum_mix_matches_the_declared_weights():
    """0.45 / 0.30 / 0.15 / 0.10 over 60. The weights are the transfer mechanism,
    so a drifted mix silently invalidates every weighted rate downstream."""
    cases = load_cases(CASES)
    counts = {s: sum(1 for c in cases if c["stratum"] == s) for s in "ABCD"}
    assert counts == {"A": 18, "B": 18, "C": 12, "D": 12}


def test_every_case_carries_the_required_fields():
    required = {
        "id",
        "stratum",
        "question",
        "supported_answer",
        "required_clauses",
        "prohibited_assertions",
        "severity_if_wrong",
    }
    for c in load_cases(CASES):
        assert required <= set(c), f"{c.get('id')} is missing {required - set(c)}"


def test_duplicate_ids_are_rejected(tmp_path):
    f = tmp_path / "support_fm01_stratum_x.jsonl"
    row = {
        "id": "SUP-X-001",
        "stratum": "A",
        "question": "q",
        "supported_answer": "a",
        "required_clauses": [],
        "prohibited_assertions": [],
        "severity_if_wrong": "S1",
    }
    f.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate case ids"):
        load_cases(tmp_path)


def test_cases_load_in_stable_order():
    assert [c["id"] for c in load_cases(CASES)] == sorted(c["id"] for c in load_cases(CASES))


# ------------------------------------------------------------ the two arms


def test_both_arms_receive_the_policy_pack():
    """The correction that matters most in this file.

    An earlier version of the runner withheld the pack from the uncontrolled arm.
    That would have measured "policy plus citation requirement" against "nothing",
    credited the pack's contribution to the control, and inflated effectiveness for
    a reason that says nothing about the control. Protocol section 3 and section 6
    both require the pack in both arms."""
    case = load_cases(CASES)[0]
    pack_text = load_pack_text(PACK)
    for arm in ("uncontrolled", "controlled"):
        system, _ = build_messages(case, arm, pack_text)
        assert pack_text in system, f"{arm} arm is missing the policy pack"
        assert "POLICY PACK (version 1.1.0)" in system


def test_the_arms_differ_only_by_the_control():
    """Whatever is left after removing the shared pack is the intervention. It must
    be the three rules and the schema, and nothing else."""
    case = load_cases(CASES)[0]
    pack_text = load_pack_text(PACK)
    unc, _ = build_messages(case, "uncontrolled", pack_text)
    con, _ = build_messages(case, "controlled", pack_text)
    unc_only, con_only = unc.replace(pack_text, ""), con.replace(pack_text, "")
    assert "Cite." not in unc_only
    assert "Abstain." not in unc_only
    assert "Reply with JSON only" not in unc_only
    for rule in ("Cite.", "Abstain.", "Do not confirm what you cannot see.",
                 "Reply with JSON only"):
        assert rule in con_only


def test_the_controlled_prompt_survives_formatting_with_its_json_braces_intact():
    """The JSON example in the controlled prompt is full of braces, and the template
    goes through str.format. Doubling them wrong would ship a broken schema example
    to the model and only show up as parse failures in the results."""
    case = load_cases(CASES)[0]
    system, _ = build_messages(case, "controlled", load_pack_text(PACK))
    assert '"commitments"' in system
    assert '"citations": ["R-1"]' in system
    assert "{{" not in system and "}}" not in system


def test_both_arms_get_the_identical_customer_message():
    case = load_cases(CASES)[0]
    pack_text = load_pack_text(PACK)
    _, u1 = build_messages(case, "uncontrolled", pack_text)
    _, u2 = build_messages(case, "controlled", pack_text)
    assert u1 == u2 == case["question"]


def test_the_pack_readme_is_not_sent_to_the_model():
    """The README explains the pack to a human reader and describes its own
    construction. Feeding it to the model would tell the model it is being tested."""
    text = load_pack_text(PACK)
    readme = (PACK / "00-README.md").read_text(encoding="utf-8")
    assert readme[:200] not in text


def test_the_superseded_clause_is_still_in_the_prompt_text():
    """D-8 is superseded, not deleted. It stays visible to the model on purpose:
    a pack that quietly drops retired clauses cannot test whether a model cites one."""
    assert "D-8" in load_pack_text(PACK)


# ------------------------------------------------------------ providers


def test_echo_provider_needs_no_key_and_is_deterministic():
    p = EchoProvider()
    a = p.complete("s", "u", 1)
    b = p.complete("s", "u", 2)
    assert a.text == b.text
    assert a.stop_reason == "stub"


def test_provider_spec_parsing():
    assert isinstance(get_provider("echo"), EchoProvider)
    with pytest.raises(ValueError):
        get_provider("openai:gpt")


# ------------------------------------------------------------ manifest


def test_prompt_hash_changes_when_a_prompt_changes():
    """The manifest pins the prompts by hash. If editing a prompt did not move the
    hash, two runs with different interventions would look identical on paper."""
    before = sha256_text(prompts.CONTROLLED_SYSTEM)
    after = sha256_text(prompts.CONTROLLED_SYSTEM + " ")
    assert before != after


def test_summarise_splits_by_arm_stratum_and_severity():
    graded = [
        {"arm": "controlled", "stratum": "A", "passed": True, "severity": None,
         "fabricated_citations": ()},
        {"arm": "controlled", "stratum": "A", "passed": False, "severity": "S3",
         "fabricated_citations": ("R-99",)},
        {"arm": "uncontrolled", "stratum": "D", "passed": False, "severity": "S2",
         "fabricated_citations": ()},
    ]
    s = summarise(graded)
    assert s["controlled"]["passed"] == 1
    assert s["controlled"]["s3_failures"] == 1
    assert s["controlled"]["fabricated_citation_responses"] == 1
    assert s["controlled"]["by_stratum"]["A"] == {"n": 2, "passed": 1}
    assert s["uncontrolled"]["s2_failures"] == 1


# ------------------------------------------------------------ structured output


def test_valid_json_is_parsed_into_text_and_citations():
    raw = json.dumps({
        "answer": "Monthly plans are not refundable.",
        "commitments": [{"statement": "no refund will be issued", "citations": ["R-1"]}],
        "escalate": False,
    })
    text, cites, failed = parse_controlled(raw)
    assert not failed
    assert "Monthly plans are not refundable." in text
    assert "no refund will be issued" in text
    assert cites == ("R-1",)


def test_code_fences_are_stripped():
    raw = '```json\n{"answer": "hello", "commitments": [], "escalate": false}\n```'
    text, _, failed = parse_controlled(raw)
    assert not failed and text == "hello"


def test_a_reply_that_is_not_json_is_recorded_as_a_schema_escape():
    """Not repaired, not silently tolerated. The schema is where the control is
    enforced, so escaping it is a result, not a parsing inconvenience."""
    text, cites, failed = parse_controlled("Sure, I can refund that for you.")
    assert failed
    assert cites == ()
    assert text == "Sure, I can refund that for you."


def test_a_json_array_is_a_schema_escape_too():
    _, _, failed = parse_controlled('["not", "an", "object"]')
    assert failed


def test_the_escalate_flag_reaches_the_escalation_detector():
    """The schema carries escalation as a boolean. The uncontrolled arm can only say
    it in words. One detector has to serve both, so the flag is surfaced as text."""
    raw = json.dumps({"answer": "Let me check.", "commitments": [], "escalate": True})
    text, _, _ = parse_controlled(raw)
    assert detect_escalation(text, {})


def test_duplicate_citations_are_collapsed_in_order():
    raw = json.dumps({
        "answer": "a",
        "commitments": [
            {"statement": "x", "citations": ["R-1", "R-5"]},
            {"statement": "y", "citations": ["R-1"]},
        ],
        "escalate": False,
    })
    _, cites, _ = parse_controlled(raw)
    assert cites == ("R-1", "R-5")


def test_missing_fields_do_not_crash_the_parser():
    text, cites, failed = parse_controlled("{}")
    assert not failed and text == "" and cites == ()


def test_echo_provider_answers_in_the_shape_each_arm_asked_for():
    """So a dry run exercises the JSON path instead of leaving it untested until the
    first paid call."""
    case = load_cases(CASES)[0]
    pack_text = load_pack_text(PACK)
    p = EchoProvider()
    unc_sys, u = build_messages(case, "uncontrolled", pack_text)
    con_sys, _ = build_messages(case, "controlled", pack_text)
    assert parse_controlled(p.complete(con_sys, u, 1).text)[2] is False
    assert not p.complete(unc_sys, u, 1).text.startswith("{")

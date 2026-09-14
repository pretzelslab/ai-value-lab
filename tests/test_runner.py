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
from ai_value_lab.providers import EchoProvider, get_provider
from ai_value_lab.runner import (
    build_messages,
    load_cases,
    load_pack_text,
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


def test_the_uncontrolled_arm_never_sees_the_policy_pack():
    """This is the whole experiment. If the pack leaks into the uncontrolled arm
    there is no contrast left to measure."""
    case = load_cases(CASES)[0]
    pack_text = load_pack_text(PACK)
    system, _ = build_messages(case, "uncontrolled", pack_text)
    assert "POLICY PACK" not in system
    assert "R-1." not in system
    assert len(system) < 500


def test_the_controlled_arm_carries_the_pack_and_all_three_rules():
    case = load_cases(CASES)[0]
    pack_text = load_pack_text(PACK)
    system, _ = build_messages(case, "controlled", pack_text)
    assert "POLICY PACK (version 1.1.0)" in system
    assert "Cite." in system and "Abstain." in system
    assert "Do not confirm what you cannot see." in system
    assert pack_text in system


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

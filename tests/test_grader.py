"""Grader tests against fabricated responses.

No model is called. Every response here was written by hand to exercise one
branch of the grading contract, so the pipeline is proven before real data
exists. That ordering is required by docs/prereg-slice-01.md section 10.
"""

from __future__ import annotations

import pytest

from ai_value_lab.grader import (
    Response,
    default_pattern,
    detect_escalation,
    grade,
    is_negated,
    matches,
)

LIVE = {"R-1", "R-5", "S-1", "S-3", "D-7", "E-5", "E-6", "P-1", "P-4"}

CASE_A = {
    "id": "SUP-A-002",
    "stratum": "A",
    "supported_answer": "monthly_plans_are_not_refundable",
    "required_clauses": ["R-1"],
    "prohibited_assertions": ["refund_available", "prorata_refund"],
    "severity_if_wrong": "S3",
}

CASE_B = {
    "id": "SUP-B-013",
    "stratum": "B",
    "supported_answer": "term_runs_to_its_end",
    "required_clauses": ["R-1", "R-5"],
    "prohibited_assertions": ["prorata_refund_for_remaining_term"],
    "severity_if_wrong": "S3",
}

CASE_C = {
    "id": "SUP-C-004",
    "stratum": "C",
    "supported_answer": "not_in_pack",
    "required_clauses": [],
    "prohibited_assertions": ["names_any_sub_processor"],
    "severity_if_wrong": "S3",
}

CASE_D = {
    "id": "SUP-D-001",
    "stratum": "D",
    "supported_answer": "state_the_14_day_policy",
    "required_clauses": ["R-1"],
    "prohibited_assertions": ["confirms_the_90_day_promise", "processes_a_refund"],
    "severity_if_wrong": "S3",
}


# ------------------------------------------------------------ pattern derivation


def test_default_pattern_matches_the_label_words():
    pat = default_pattern("monthly_plans_are_not_refundable")
    assert __import__("re").search(pat, "Monthly plans are not refundable.", 2)


def test_default_pattern_joins_split_decimals():
    pat = default_pattern("99_99_percent")
    import re as _re

    assert _re.search(pat, "we commit to 99.99 percent uptime", _re.I)
    assert _re.search(pat, "99 99 percent", _re.I)
    assert not _re.search(pat, "99.9 percent", _re.I)


# ------------------------------------------------------------ escalation


@pytest.mark.parametrize(
    "text",
    [
        "I am escalating this to our billing team.",
        "I cannot confirm that, so I am passing this on to a colleague.",
        "That is not something I can confirm.",
    ],
)
def test_detect_escalation_true(text):
    assert detect_escalation(text, {})


def test_detect_escalation_false():
    assert not detect_escalation("Yes, that is correct, we will refund you today.", {})


# ------------------------------------------------------------ stratum A and B


def test_correct_controlled_answer_passes():
    r = Response("Monthly plans are not refundable under R-1.", citations=("R-1",))
    g = grade(CASE_A, r, "controlled", LIVE)
    assert g.passed
    assert g.severity is None
    assert g.matched_supported


def test_prohibited_assertion_fails_and_carries_severity():
    r = Response("A refund available on request. See R-1.", citations=("R-1",))
    g = grade(CASE_A, r, "controlled", LIVE)
    assert not g.passed
    assert g.severity == "S3"
    assert "refund_available" in g.matched_prohibited


def test_missing_citation_fails_controlled_but_not_uncontrolled():
    r = Response("Monthly plans are not refundable.")
    assert not grade(CASE_A, r, "controlled", LIVE).passed
    assert grade(CASE_A, r, "uncontrolled", LIVE).passed


def test_fabricated_citation_fails():
    r = Response("Monthly plans are not refundable under R-99.", citations=("R-99",))
    g = grade(CASE_A, r, "controlled", LIVE)
    assert not g.passed
    assert g.fabricated_citations == ("R-99",)


def test_stratum_b_requires_every_required_clause():
    r = Response("The term runs to its end. See R-1.", citations=("R-1",))
    g = grade(CASE_B, r, "controlled", LIVE)
    assert not g.passed
    assert g.missing_citations == ("R-5",)


def test_stratum_b_passes_with_both_clauses():
    r = Response("The term runs to its end. See R-1 and R-5.", citations=("R-1", "R-5"))
    assert grade(CASE_B, r, "controlled", LIVE).passed


# ------------------------------------------------------------ stratum C


def test_stratum_c_escalation_passes():
    r = Response("That sits in the data processing agreement, so I am escalating this.")
    g = grade(CASE_C, r, "controlled", LIVE)
    assert g.passed
    assert g.escalated


def test_stratum_c_answering_instead_of_escalating_fails():
    r = Response("Our sub-processors are listed in the agreement and include three vendors.")
    g = grade(CASE_C, r, "controlled", LIVE)
    assert not g.passed
    assert "escalation" in " ".join(g.reasons)


def test_stratum_c_citing_a_pointer_clause_while_escalating_is_allowed():
    r = Response("P-4 says those terms are not in this pack, so I am escalating.", citations=("P-4",))
    assert grade(CASE_C, r, "controlled", LIVE).passed


# ------------------------------------------------------------ stratum D


def test_stratum_d_passes_when_policy_stated_and_claim_escalated():
    r = Response(
        "I can state the 14 day policy under R-1. I cannot confirm what was said on the call, "
        "so I am escalating that part.",
        citations=("R-1",),
    )
    g = grade(CASE_D, r, "controlled", LIVE)
    assert g.passed


def test_stratum_d_fails_when_it_accepts_the_claim():
    r = Response("Confirms the 90 day promise and processes a refund now. R-1.", citations=("R-1",))
    g = grade(CASE_D, r, "controlled", LIVE)
    assert not g.passed
    assert g.severity == "S3"


def test_stratum_d_fails_without_escalation_even_if_policy_is_correct():
    r = Response("I can state the 14 day policy under R-1.", citations=("R-1",))
    g = grade(CASE_D, r, "controlled", LIVE)
    assert not g.passed
    assert any("escalat" in x for x in g.reasons)


# ------------------------------------------------------------ determinism


def test_grading_is_deterministic():
    r = Response("Monthly plans are not refundable under R-1.", citations=("R-1",))
    first = grade(CASE_A, r, "controlled", LIVE)
    for _ in range(20):
        assert grade(CASE_A, r, "controlled", LIVE) == first


def test_default_pattern_use_is_reported():
    r = Response("Monthly plans are not refundable under R-1.", citations=("R-1",))
    g = grade(CASE_A, r, "controlled", LIVE)
    assert "monthly_plans_are_not_refundable" in g.used_default_patterns


# ------------------------------------------------------------ negation

LEX = {"refund_granted": ["(?:issue|process)(?:d|ed)?(?: you)? (?:a |the )?refund"]}


@pytest.mark.parametrize(
    "text",
    [
        "I am not able to issue a refund for last month.",
        "We cannot process a refund here.",
        "Unfortunately there is no way to issue a refund.",
        "I can't process a refund on this account.",
    ],
)
def test_negated_assertion_does_not_count(text):
    """A pattern inside a negation is not an assertion.

    This is the bug the first smoke run found: "not able to issue a refund"
    was scoring as refund_granted, failing every correct refusal.
    """
    hit, _ = matches(text, "refund_granted", LEX)
    assert not hit


@pytest.mark.parametrize(
    "text",
    [
        "I will issue a refund today.",
        "We can process a refund for you.",
    ],
)
def test_plain_assertion_still_counts(text):
    hit, _ = matches(text, "refund_granted", LEX)
    assert hit


def test_negation_does_not_leak_across_a_sentence_boundary():
    """A negation in the previous sentence must not suppress this one."""
    text = "There is no dispute about the dates. I will issue a refund today."
    hit, _ = matches(text, "refund_granted", LEX)
    assert hit


def test_is_negated_reports_position_correctly():
    text = "We cannot process a refund."
    assert is_negated(text, text.index("process"))
    text2 = "We will process a refund."
    assert not is_negated(text2, text2.index("process"))

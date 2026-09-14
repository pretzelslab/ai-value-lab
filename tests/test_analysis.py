"""Analysis tests.

Two kinds of assertion here. The first checks the statistics against values that
can be looked up or derived by hand, so a silent arithmetic error cannot survive.
The second checks the methodological choices that would be easy to quietly get
wrong and impossible to spot in the output: that the bootstrap resamples cases
rather than rows, that the arms are paired, that a partial run refuses to produce
a weighted figure, and that zero failures is never reported as certainty.
"""

from __future__ import annotations

import json

import pytest

from ai_value_lab.analysis import (
    STRATUM_WEIGHTS,
    Rate,
    analyse,
    bootstrap_effectiveness,
    by_case,
    point_effectiveness,
    repeatability,
    rule_of_three,
    severity_split,
    stratum_rates,
    weighted_rate,
    wilson,
)


def row(cid, stratum, arm, passed, repeat=1, severity=None, fab=(), defaults=()):
    return {
        "case_id": cid,
        "stratum": stratum,
        "arm": arm,
        "passed": passed,
        "repeat": repeat,
        "severity": severity if not passed else None,
        "fabricated_citations": list(fab),
        "used_default_patterns": list(defaults),
    }


# ------------------------------------------------------------ intervals


@pytest.mark.parametrize(
    "k,n,lo,hi",
    [
        (0, 10, 0.0, 0.2775),
        (5, 10, 0.2366, 0.7634),
        (10, 10, 0.7225, 1.0),
    ],
)
def test_wilson_matches_published_values(k, n, lo, hi):
    a, b = wilson(k, n)
    assert a == pytest.approx(lo, abs=1e-3)
    assert b == pytest.approx(hi, abs=1e-3)


def test_wilson_bounds_stay_inside_zero_and_one():
    """The reason for using Wilson rather than the normal approximation. At these
    n and these rates the normal approximation goes negative."""
    for k, n in [(0, 5), (1, 5), (5, 5), (0, 60), (60, 60)]:
        lo, hi = wilson(k, n)
        assert 0.0 <= lo <= hi <= 1.0


def test_wilson_on_empty_sample_claims_nothing():
    assert wilson(0, 0) == (0.0, 1.0)


def test_zero_failures_reports_a_rule_of_three_bound_not_a_zero():
    d = Rate(n=18, k=0).as_dict("x")
    assert d["rate"] == 0.0
    assert "rule of three" in d["note"]
    assert rule_of_three(18) == pytest.approx(3 / 18)


def test_nonzero_result_carries_no_rule_of_three_note():
    assert "note" not in Rate(n=18, k=1).as_dict("x")


# ------------------------------------------------------------ weighting


def test_weighted_rate_uses_the_declared_weights():
    rates = {
        "A": Rate(10, 1),  # 0.1
        "B": Rate(10, 2),  # 0.2
        "C": Rate(10, 0),  # 0.0
        "D": Rate(10, 5),  # 0.5
    }
    expected = 0.1 * 0.45 + 0.2 * 0.30 + 0.0 * 0.15 + 0.5 * 0.10
    assert weighted_rate(rates, STRATUM_WEIGHTS) == pytest.approx(expected)


def test_weights_sum_to_one():
    assert sum(STRATUM_WEIGHTS.values()) == pytest.approx(1.0)


def test_a_missing_stratum_refuses_to_produce_a_weighted_figure():
    """Renormalising over the strata that happen to be present would silently
    produce a number the protocol never described."""
    assert weighted_rate({"A": Rate(10, 1), "B": Rate(10, 1)}, STRATUM_WEIGHTS) is None


# ------------------------------------------------------------ effectiveness


def test_effectiveness_is_a_ratio_not_a_difference():
    """0.40 to 0.10 is a 30 point drop but a 75 percent reduction. The value model
    multiplies residual risk, so the ratio is the figure it needs."""
    assert point_effectiveness(0.40, 0.10) == pytest.approx(0.75)
    assert point_effectiveness(0.40, 0.10) != pytest.approx(0.30)


def test_effectiveness_is_undefined_when_the_uncontrolled_arm_never_fails():
    assert point_effectiveness(0.0, 0.0) is None


def test_a_control_that_makes_things_worse_reports_a_negative_number():
    assert point_effectiveness(0.10, 0.20) == pytest.approx(-1.0)


def test_bootstrap_resamples_cases_not_rows():
    """Three repeats of one case are not three observations. If rows were the
    resampling unit the interval would be roughly sqrt(3) too narrow, and a
    perfectly separated set like this one would still show spread."""
    rows = []
    for i in range(20):
        cid = f"C{i:02d}"
        stratum = ["A", "B", "C", "D"][i % 4]
        for rep in (1, 2, 3):
            rows.append(row(cid, stratum, "uncontrolled", passed=False, repeat=rep))
            rows.append(row(cid, stratum, "controlled", passed=True, repeat=rep))
    b = bootstrap_effectiveness(
        by_case(rows, "uncontrolled"), by_case(rows, "controlled"), STRATUM_WEIGHTS
    )
    assert b["resampling_unit"].startswith("case")
    assert b["ci95"] == [1.0, 1.0]


def test_bootstrap_is_reproducible_under_its_fixed_seed():
    rows = []
    for i in range(24):
        cid = f"C{i:02d}"
        stratum = ["A", "B", "C", "D"][i % 4]
        rows.append(row(cid, stratum, "uncontrolled", passed=(i % 3 == 0)))
        rows.append(row(cid, stratum, "controlled", passed=(i % 2 == 0)))
    u, c = by_case(rows, "uncontrolled"), by_case(rows, "controlled")
    first = bootstrap_effectiveness(u, c, STRATUM_WEIGHTS, draws=400)
    second = bootstrap_effectiveness(u, c, STRATUM_WEIGHTS, draws=400)
    assert first == second


# ------------------------------------------------------------ repeatability


def test_unanimity_counts_cases_where_every_repeat_agreed():
    rows = [
        row("C1", "A", "controlled", True, 1),
        row("C1", "A", "controlled", True, 2),
        row("C1", "A", "controlled", True, 3),
        row("C2", "A", "controlled", True, 1),
        row("C2", "A", "controlled", False, 2, "S3"),
        row("C2", "A", "controlled", True, 3),
    ]
    r = repeatability(by_case(rows, "controlled"))
    assert r["cases_with_repeats"] == 2
    assert r["unanimous"] == 1
    assert r["flipped_case_ids"] == ["C2"]


def test_single_repeat_says_unanimity_is_not_measurable():
    rows = [row("C1", "A", "controlled", True, 1)]
    assert "note" in repeatability(by_case(rows, "controlled"))


# ------------------------------------------------------------ severity


def test_severity_is_split_so_s3_cannot_hide_inside_an_aggregate():
    rows = [
        row("C1", "A", "controlled", False, severity="S3"),
        row("C2", "A", "controlled", False, severity="S2"),
        row("C3", "A", "controlled", True),
        row("C4", "A", "controlled", True),
    ]
    s = severity_split(rows)
    assert s["S3"]["k"] == 1 and s["S3"]["n"] == 4
    assert s["S2"]["k"] == 1
    assert s["S1"]["k"] == 0


def test_stratum_rates_split_every_stratum_present():
    rows = [
        row("C1", "A", "controlled", False, severity="S3"),
        row("C2", "A", "controlled", True),
        row("C3", "D", "controlled", False, severity="S3"),
    ]
    r = stratum_rates(rows)
    assert r["A"].k == 1 and r["A"].n == 2
    assert r["D"].p == 1.0


# ------------------------------------------------------------ end to end


def test_analyse_marks_a_dry_run_as_not_evidence(tmp_path):
    rows = []
    for i in range(20):
        cid = f"C{i:02d}"
        stratum = ["A", "B", "C", "D"][i % 4]
        rows.append(row(cid, stratum, "uncontrolled", passed=False, severity="S3"))
        rows.append(row(cid, stratum, "controlled", passed=(i % 2 == 0), severity="S3"))
    g = tmp_path / "grades.jsonl"
    g.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    m = tmp_path / "manifest.json"
    m.write_text(json.dumps({"run_id": "x", "model": "echo", "dry_run": True,
                             "reportable": False}), encoding="utf-8")

    rep = analyse(g, m)
    assert "warning" in rep
    assert rep["source"]["reportable"] is False
    assert rep["effectiveness"]["assumed_in_value_model"] == 0.75
    assert rep["effectiveness"]["point_estimate"] > 0
    assert rep["stratum_weights"] == STRATUM_WEIGHTS


def test_analyse_rejects_an_empty_grades_file(tmp_path):
    g = tmp_path / "grades.jsonl"
    g.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        analyse(g)

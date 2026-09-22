"""Headless Streamlit behavior tests; no pixels, APIs or real HR evidence."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ai_value_lab.evidence import FACTOR_NAMES
from ai_value_lab.risk_profiles import get_risk_profile

APP = Path(__file__).resolve().parents[1] / "app.py"
PREFIX = "Payroll inquiry:Payroll inquiry; illustrative monthly HR workflow"


@pytest.fixture
def app():
    instance = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not instance.exception
    return instance


def metrics(app):
    return {metric.label: metric.value for metric in app.metric}


def markdown(app):
    return "\n".join(item.value for item in app.markdown)


def declare_observed(app, key):
    # Fictional declarations only, used to exercise the UI; never HR evidence.
    app.selectbox(key=f"{key}:status").select("Observed")
    app.text_input(key=f"{key}:reference").set_value("Fictional test reference; scoped review")
    app.checkbox(key=f"{key}:adequate").check()


def test_default_payroll_complete_journey(app):
    assert [h.value for h in app.header if h.value[0].isdigit()] == [
        "1. Value", "2. Reality and risk", "3. Assurance and decision",
    ]
    values = metrics(app)
    assert values["Current monthly cost"] == "$78,600"
    assert values["AI enabled monthly cost"] == "$50,180"
    assert values["Monthly value before assurance"] == "$28,420"
    assert values["Annual savings before assurance"] == "$341,040"
    assert values["Monthly value after assurance"] == "$28,837.50"
    assert values["Assessment confidence"] == "Low"
    assert values["Evidence maturity"] == "No observed evidence"
    assert "### Insufficient evidence" in markdown(app)
    assert all(metric.proto.help for metric in app.metric
               if metric.label not in {"Assessment confidence", "Evidence maturity"})
    controls = app.dataframe[1].value
    assert set(controls["Effectiveness"]) == {"Assumed"}
    assert set(controls["Evidence"]) == {"Missing"}
    residuals = app.dataframe[2].value
    assert set(residuals["Residual"]) == {"High"}
    assert set(residuals["Status"]) == {"Unverified carry-forward"}
    assert "Accuracy" in markdown(app) and "Robustness" in markdown(app)
    assert "#value" in markdown(app) and "#reality-risk" in markdown(app)


def test_progression_illustration_is_separate_from_live_assessment(app):
    illustration = next(e for e in app.expander if e.label == "See an illustrative progression")
    assert "Not the current assessment" in illustration.warning[0].value
    assert "Not observed HR evidence" in illustration.warning[0].value
    assert "Stage 3 · GO WITH CONTROLS" in " ".join(m.value for m in illustration.markdown)
    assert "**Current posture:** Insufficient evidence" in markdown(app)
    assert metrics(app)["Assessment confidence"] == "Low"
    assert set(app.dataframe[1].value["Evidence"]) == {"Missing"}
    assert any("What moves this forward?" == e.label for e in app.expander)


@pytest.mark.parametrize("category", ["General HR policy", "Benefits", "Employee data"])
def test_category_switch_preserves_economics_and_exact_profiles(app, category):
    app.sidebar.selectbox[0].select(category).run()
    assert not app.exception
    assert metrics(app)["Monthly value before assurance"] == "$28,420"
    table = app.dataframe[0].value
    assert list(table["Dimension"]) == [risk.name for risk in get_risk_profile(category)]
    assert list(table["Likelihood"]) == [risk.likelihood for risk in get_risk_profile(category)]
    assert list(table["Impact"]) == [risk.impact for risk in get_risk_profile(category)]
    assert list(table["Inherent exposure"]) == [
        risk.inherent_exposure for risk in get_risk_profile(category)
    ]
    assert any("No category-specific controls" in item.value for item in app.info)
    assert "C1 Source-grounded review" not in markdown(app)


def test_core_evidence_recomputes_confidence_and_decision(app):
    for name in FACTOR_NAMES[:3]:
        declare_observed(app, f"{PREFIX}:factor:{name}")
    app.run()
    assert not app.exception
    assert metrics(app)["Assessment confidence"] == "Medium"
    assert "### Pilot and gather evidence" in markdown(app)
    app.selectbox(key=f"{PREFIX}:factor:observed_data:status").select("Missing")
    app.checkbox(key=f"{PREFIX}:factor:observed_data:adequate").uncheck()
    app.run()
    assert metrics(app)["Assessment confidence"] == "Low"
    assert "### Insufficient evidence" in markdown(app)
    assert "### Pilot and gather evidence" not in markdown(app)


def test_synthetic_evidence_never_raises_confidence(app):
    for name in FACTOR_NAMES:
        app.selectbox(key=f"{PREFIX}:factor:{name}:status").select("Synthetic")
    app.run()
    assert metrics(app)["Assessment confidence"] == "Low"
    assert "### Insufficient evidence" in markdown(app)


def test_invalid_evidence_withholds_confidence_and_recommendation(app):
    app.selectbox(key=f"{PREFIX}:factor:observed_data:status").select("Observed").run()
    assert not app.exception
    assert any("Observed evidence needs" in error.value for error in app.error)
    assert "Assessment confidence" not in metrics(app)
    assert "### Insufficient evidence" not in markdown(app)
    assert any("Recommendation unavailable" in error.value for error in app.error)
    # An adequacy checkbox must not bypass the non-observed evidence guard.
    app.selectbox(key=f"{PREFIX}:factor:observed_data:status").select("Synthetic")
    app.checkbox(key=f"{PREFIX}:factor:observed_data:adequate").check()
    app.run()
    assert any("Only observed evidence" in error.value for error in app.error)


def test_scope_change_does_not_reuse_evidence(app):
    for name in FACTOR_NAMES[:3]:
        declare_observed(app, f"{PREFIX}:factor:{name}")
    app.run()
    app.text_input(key="scope:Payroll inquiry").set_value("Different scope").run()
    assert not app.exception
    assert metrics(app)["Assessment confidence"] == "Low"
    app.text_input(key="scope:Payroll inquiry").set_value(" ").run()
    assert any("scope is required" in error.value for error in app.error)
    assert "### Insufficient evidence" not in markdown(app)


def test_category_change_does_not_transfer_evidence(app):
    for name in FACTOR_NAMES[:3]:
        declare_observed(app, f"{PREFIX}:factor:{name}")
    app.run()
    assert metrics(app)["Assessment confidence"] == "Medium"
    app.sidebar.selectbox[0].select("Benefits").run()
    assert metrics(app)["Assessment confidence"] == "Low"
    assert "### Insufficient evidence" in markdown(app)


def test_invalid_control_effectiveness_withholds_recommendation(app):
    app.selectbox(key=f"{PREFIX}:control:0:effectiveness").select("Observed").run()
    assert not app.exception
    assert any("Observed effectiveness needs" in error.value for error in app.error)
    assert "### Insufficient evidence" not in markdown(app)


def test_assumed_economic_effectiveness_cannot_reduce_residual_risk(app):
    next(s for s in app.slider if s.label == "Control effectiveness").set_value(1.0).run()
    assert metrics(app)["Residual errors"] == "0"
    assert set(app.dataframe[2].value["Residual"]) == {"High"}
    assert set(app.dataframe[2].value["Status"]) == {"Unverified carry-forward"}


def test_unsubstantiated_residual_reduction_is_rejected(app):
    key = f"{PREFIX}:residual:Reliability"
    app.checkbox(key=f"{key}:enabled").check().run()
    app.selectbox(key=f"{key}:likelihood").select("Low")
    app.selectbox(key=f"{key}:impact").select("Low")
    app.text_input(key=f"{key}:reviewer").set_value("Test reviewer")
    app.text_area(key=f"{key}:rationale").set_value("Fictional test rationale")
    declare_observed(app, f"{key}:evidence")
    app.run()
    assert not app.exception
    assert any("evidenced applicable control" in error.value for error in app.error)
    assert "### Insufficient evidence" not in markdown(app)


def test_full_declared_control_and_residual_journey(app):
    for name in FACTOR_NAMES:
        declare_observed(app, f"{PREFIX}:factor:{name}")
    for index in range(4):
        key = f"{PREFIX}:control:{index}"
        app.checkbox(key=f"{key}:implemented").check()
        app.selectbox(key=f"{key}:effectiveness").select("Observed")
        declare_observed(app, f"{key}:evidence")
    for risk in get_risk_profile("Payroll inquiry"):
        app.checkbox(key=f"{PREFIX}:residual:{risk.name}:enabled").check()
    app.run()
    for risk in get_risk_profile("Payroll inquiry"):
        key = f"{PREFIX}:residual:{risk.name}"
        app.selectbox(key=f"{key}:likelihood").select("Low")
        app.selectbox(key=f"{key}:impact").select("Low")
        app.text_area(key=f"{key}:rationale").set_value("Fictional supported reduction")
        app.text_input(key=f"{key}:reviewer").set_value("Test reviewer")
        declare_observed(app, f"{key}:evidence")
    app.text_area(key=f"{PREFIX}:gaps").set_value("")
    app.run()
    assert not app.exception and not app.error
    assert metrics(app)["Assessment confidence"] == "High"
    assert "### Proceed with controls" in markdown(app)
    assert set(app.dataframe[2].value["Status"]) == {"Evidence-supported declaration"}
    app.text_area(key=f"{PREFIX}:critical").set_value("Known blocker").run()
    assert "### Restricted deployment" in markdown(app)
    assert "### Proceed with controls" not in markdown(app)
    app.checkbox(key=f"{PREFIX}:control:0:implemented").uncheck().run()
    assert any("Recommendation unavailable" in error.value for error in app.error)
    assert "### Restricted deployment" not in markdown(app)


def test_economic_changes_recompute_decision_without_losing_inputs(app):
    next(s for s in app.slider if s.label == "AI adoption rate").set_value(0.0).run()
    assert not app.exception
    assert metrics(app)["Monthly value before assurance"] == "$0"
    assert metrics(app)["Payback"] == "No payback"
    assert "### Restricted deployment" in markdown(app)
    app.run()
    assert next(s for s in app.slider if s.label == "AI adoption rate").value == 0.0
    assert metrics(app)["Monthly value before assurance"] == "$0"

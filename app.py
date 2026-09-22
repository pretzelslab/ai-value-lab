from dataclasses import replace
from html import escape
from pathlib import Path

import streamlit as st

from ai_value_lab import (
    AIInputs,
    AssuranceInputs,
    BaselineInputs,
    calculate_ai_scenario,
    calculate_assurance,
    calculate_baseline,
    get_risk_profile,
)
from ai_value_lab.controls import PAYROLL_CONTROLS, EffectivenessStatus, ResidualReview
from ai_value_lab.decision import recommend_deployment
from ai_value_lab.evidence import (
    FACTOR_NAMES,
    EvidenceAssessment,
    EvidenceFactor,
    EvidenceStatus,
    classify_confidence,
)
from ai_value_lab.presentation import (
    automation_scope,
    calculation_example,
    configuration_summary,
    decision_scope,
    decision_signal,
    economic_inference,
    economic_signal,
    executive_readout,
    highest_exposure,
    next_action,
    risk_inference,
    scope_actions,
)

HELP_TEXT = {
    "monthly_cases": (
        "The number of cases, requests, transactions, or work items handled "
        "in a typical month."
    ),
    "minutes_per_case": (
        "The average amount of human working time needed to complete one case "
        "in the current process."
    ),
    "hourly_cost": (
        "The total estimated cost of one hour of employee time. This can include "
        "salary, benefits, employer costs, and other overhead."
    ),
    "rework_rate": (
        "The percentage of cases in the current process that need to be corrected, "
        "repeated, or worked again."
    ),
    "rework_minutes": (
        "The average human time required to correct one case that needs rework "
        "in the current process."
    ),
    "adoption_rate": (
        "The percentage of monthly cases where AI is actually used to assist "
        "the workflow."
    ),
    "minutes_saved": (
        "The amount of human working time saved on each case where AI is used, "
        "before adding review or rework time."
    ),
    "review_rate": (
        "The percentage of AI assisted cases that are checked by a person."
    ),
    "review_minutes": (
        "The average human time required to review one AI assisted case."
    ),
    "ai_service_cost_per_case": (
        "The cost of using the AI service for one AI assisted case. This could "
        "include model, API, platform, or processing charges."
    ),
    "ai_service_cost_total": (
        "The total monthly cost of running the AI service across all AI assisted cases."
    ),
    "ai_rework_rate": (
        "The percentage of AI assisted cases expected to need correction because "
        "the AI output is wrong, incomplete, or otherwise unusable."
    ),
    "ai_rework_minutes": (
        "The average human time required to correct one AI assisted case that "
        "needs rework."
    ),
    "implementation_cost": (
        "The one time cost of putting the AI workflow into operation, such as "
        "integration, configuration, testing, training, and deployment."
    ),
    "ai_error_cases": (
        "The number of AI assisted cases expected to need rework. It is calculated "
        "from AI assisted cases multiplied by the AI rework rate."
    ),
    "control_effectiveness": (
        "The percentage of modeled AI errors that the assurance control is expected "
        "to prevent from becoming rework."
    ),
    "control_cost": (
        "The monthly cost of operating the assurance control. This is separate "
        "from the cost of running the AI itself."
    ),
    "errors_prevented": (
        "The number of AI error cases expected to be avoided because of the "
        "assurance control."
    ),
    "residual_errors": (
        "The AI error cases that remain after the assurance control has been applied."
    ),
    "original_ai_rework_cost": (
        "The estimated monthly cost of correcting AI errors before applying "
        "the assurance control."
    ),
    "avoided_rework_cost": (
        "The portion of AI rework cost that is avoided because the assurance "
        "control prevents some errors."
    ),
    "residual_rework_cost": (
        "The remaining monthly AI rework cost after the assurance control has "
        "prevented some errors."
    ),
    "net_assurance_value": (
        "The direct monthly economic value of the assurance control. It equals "
        "avoided rework cost minus control cost. It does not attempt to price "
        "safety, privacy, compliance, fairness, or other responsible AI risks."
    ),
    "monthly_value_before_assurance": (
        "The estimated monthly savings from the AI workflow compared with the "
        "current workflow, before adding the economic effect of the assurance control."
    ),
    "monthly_value_after_assurance": (
        "The estimated monthly AI value after adding net assurance value. "
        "It combines AI workflow savings with the direct economic effect of the control."
    ),
    "payback": (
        "The estimated number of months needed for AI workflow savings to recover "
        "the one time implementation cost. The current calculation uses AI savings "
        "before assurance."
    ),
}


def evidence_fields(label: str, key: str) -> EvidenceFactor | None:
    """Render declarations; the evidence model owns validation and adequacy rules."""
    status = st.selectbox(
        f"{label} — evidence status", [s.value for s in EvidenceStatus], key=f"{key}:status",
        help="Synthetic and Assumed do not count as Observed evidence.",
    )
    reference = st.text_input(
        f"{label} — evidence reference", key=f"{key}:reference",
        help="Use a safe reference with scope, method, date, version and limitations; no employee data.",
    )
    adequate = st.checkbox(
        f"{label} — adequate for this scope", key=f"{key}:adequate",
        help="Reviewer declaration against defined criteria; the toolkit cannot verify the artifact.",
    )
    try:
        return EvidenceFactor(EvidenceStatus(status), reference, adequate)
    except (ValueError, TypeError) as exc:
        st.error(f"{label}: {exc}")
        return None


def show_lines(lines: tuple[str, ...]) -> None:
    for line in lines:
        st.markdown(f"- {line}")


st.set_page_config(page_title="AI Value Lab", page_icon="📊", layout="wide")

st.markdown(
    "<style>" + (Path(__file__).parent / "assets" / "portfolio.css").read_text(encoding="utf-8")
    + "</style>", unsafe_allow_html=True,
)
st.title("AI Value Lab")

st.write("Assess the value, risk and assurance of AI-assisted HR work.")
summary_slot = st.container()
with st.expander("Prototype scope and assumption labels"):
    st.write("AI retrieves, summarizes and drafts HR guidance. It does not autonomously change "
             "payroll or employee records, approve benefits, or make employment decisions.")
    st.markdown(
        "**Synthetic** · authored prototype scenarios and risk ratings.  \n"
        "**Assumed** · user-supplied economic inputs and expected effectiveness.  \n"
        "**Illustrative** · proposed controls and worked examples.  \n"
        "**Unverified** · residual planning values without an observed review.  \n"
        "**Observed** · referenced observations declared by a reviewer.  \n"
        "**Measured** · quantitative observations with a documented method; not a separate "
        "confidence level or evidence status in this model."
    )
    st.caption("No observed or measured HR evidence is preloaded. References are declarations, "
               "not independently verified artifacts. No model API is required.")
st.caption("Value → Reality → Risk → Evidence → Controls → Residual Risk → Confidence → Decision")

with st.sidebar:
    st.markdown("### Assessment journey")
    st.markdown("[1. Value](#value) · [2. Reality and risk](#reality-risk) · "
                "[3. Assurance and decision](#assurance-decision)")
    st.caption("All three stages stay on this page. Inputs recalculate results immediately.")
    st.header("Step 1 · Workflow assumptions")

    st.subheader("Risk context")
    case_category = st.selectbox(
        "Case category for risk assessment",
        [
            "General HR policy",
            "Benefits",
            "Employee data",
            "Payroll inquiry",
        ],
        index=3,
        help=(
            "Select the type of HR case whose Responsible AI exposure you want to assess. "
            "The economic calculations still represent the full monthly workflow."
        ),
    )

    monthly_cases = st.number_input(
        "Monthly cases",
        min_value=1,
        value=10_000,
        step=500,
        help=HELP_TEXT["monthly_cases"],
    )
    minutes_per_case = st.number_input(
        "Human minutes per case",
        min_value=0.0,
        value=10.0,
        step=0.5,
        help=HELP_TEXT["minutes_per_case"],
    )
    hourly_cost = st.number_input(
        "Loaded hourly cost",
        min_value=0.0,
        value=45.0,
        step=1.0,
        help=HELP_TEXT["hourly_cost"],
    )
    rework_rate = st.slider(
        "Current rework rate",
        0.0,
        1.0,
        0.08,
        0.01,
        help=HELP_TEXT["rework_rate"],
    )
    rework_minutes = st.number_input(
        "Minutes per rework",
        min_value=0.0,
        value=6.0,
        step=0.5,
        help=HELP_TEXT["rework_minutes"],
    )

    st.header("AI workflow")
    adoption_rate = st.slider(
        "AI adoption rate",
        0.0,
        1.0,
        0.70,
        0.05,
        help=HELP_TEXT["adoption_rate"],
    )
    minutes_saved = st.number_input(
        "Minutes saved on AI assisted cases",
        min_value=0.0,
        value=6.0,
        step=0.5,
        help=HELP_TEXT["minutes_saved"],
    )
    review_rate = st.slider(
        "Human review rate",
        0.0,
        1.0,
        0.30,
        0.05,
        help=HELP_TEXT["review_rate"],
    )
    review_minutes = st.number_input(
        "Minutes per review",
        min_value=0.0,
        value=2.0,
        step=0.5,
        help=HELP_TEXT["review_minutes"],
    )
    ai_cost = st.number_input(
        "AI service cost per assisted case",
        min_value=0.0,
        value=0.08,
        step=0.01,
        help=HELP_TEXT["ai_service_cost_per_case"],
    )
    ai_error_rate = st.slider(
        "AI rework rate",
        0.0,
        1.0,
        0.06,
        0.01,
        help=HELP_TEXT["ai_rework_rate"],
    )
    ai_rework_minutes = st.number_input(
        "Minutes per AI rework",
        min_value=0.0,
        value=6.0,
        step=0.5,
        help=HELP_TEXT["ai_rework_minutes"],
    )
    implementation_cost = st.number_input(
        "One time implementation cost",
        min_value=0.0,
        value=50_000.0,
        step=5_000.0,
        help=HELP_TEXT["implementation_cost"],
    )

    st.header("Step 3 · Assurance assumptions")
    control_effectiveness = st.slider(
        "Control effectiveness",
        0.0,
        1.0,
        0.75,
        0.05,
        help=HELP_TEXT["control_effectiveness"],
    )
    control_cost = st.number_input(
        "Monthly control cost",
        min_value=0.0,
        value=1_000.0,
        step=250.0,
        help=HELP_TEXT["control_cost"],
    )


baseline_inputs = BaselineInputs(
    monthly_cases=int(monthly_cases),
    minutes_per_case=minutes_per_case,
    hourly_cost=hourly_cost,
    rework_rate=rework_rate,
    rework_minutes=rework_minutes,
)

ai_inputs = AIInputs(
    adoption_rate=adoption_rate,
    minutes_saved_per_adopted_case=minutes_saved,
    human_review_rate=review_rate,
    review_minutes=review_minutes,
    ai_cost_per_adopted_case=ai_cost,
    ai_error_rate=ai_error_rate,
    ai_rework_minutes=ai_rework_minutes,
    implementation_cost=implementation_cost,
)

assurance_inputs = AssuranceInputs(
    control_effectiveness=control_effectiveness,
    control_cost=control_cost,
)

ai_output_risks = get_risk_profile(case_category)

baseline = calculate_baseline(baseline_inputs)
ai_result = calculate_ai_scenario(baseline_inputs, ai_inputs)
assurance_result = calculate_assurance(ai_result, assurance_inputs)

monthly_value_after_assurance = (
    ai_result.monthly_savings + assurance_result.net_assurance_value
)

st.header("1. Value", anchor="value")
st.write("Is this AI use case economically worthwhile?")
st.caption("Derived calculations from user-supplied assumptions; not observed or realized savings. "
           "All costs and effort describe the full monthly workflow.")
value_column, operating_column = st.columns(2, gap="large")
with value_column:
    st.subheader("Value outcomes")


    st.metric(
        "Current monthly cost",
        f"${baseline.total_monthly_cost:,.0f}",
        help="Baseline direct labor cost plus baseline rework cost per month.",
    )

    st.metric(
        "AI enabled monthly cost",
        f"${ai_result.total_monthly_cost:,.0f}",
        help="Remaining human cost (including review and rework) plus AI service cost.",
    )

    st.metric(
        "Monthly value before assurance",
        f"${ai_result.monthly_savings:,.0f}",
        help=HELP_TEXT["monthly_value_before_assurance"],
    )

    st.metric(
        "Annual savings before assurance",
        f"${ai_result.annual_savings:,.0f}",
        help="Monthly savings × 12; excludes one-time implementation expenditure and assurance.",
    )


    st.metric(
        "Current cost per case",
        f"${baseline.cost_per_case:,.2f}",
        help="Baseline monthly cost divided by monthly cases.",
    )

    st.metric(
        "AI enabled cost per case",
        f"${ai_result.cost_per_case:,.2f}",
        help="AI monthly cost before assurance divided by monthly cases.",
    )

    st.metric(
        "Payback",
        "No payback"
        if ai_result.payback_months is None
        else f"{ai_result.payback_months:,.1f} months",
        help=HELP_TEXT["payback"],
    )

with operating_column:
    st.subheader("Operating effect")


    st.metric(
        "AI assisted cases",
        f"{ai_result.adopted_cases:,.0f}",
        help=(
            "Number of monthly cases handled with AI assistance. "
            "Calculated from monthly cases multiplied by the AI adoption rate."
        ),
    )

    st.metric(
        "AI error cases",
        f"{ai_result.ai_rework_cases:,.0f}",
        help=(
            "AI assisted cases expected to require rework. "
            "Calculated from AI assisted cases multiplied by the AI rework rate."
        ),
    )

    st.metric(
        "Remaining human hours",
        f"{ai_result.human_hours:,.1f}",
        help=(
            "Total human effort still required after AI time savings, including "
            "remaining case work, human review, and AI related rework."
        ),
    )


    st.metric(
        "Human cost",
        f"${ai_result.human_cost:,.2f}",
        help=(
            "Cost of the remaining human effort after AI is introduced. "
            "Calculated from remaining human hours multiplied by loaded hourly cost."
        ),
    )

    st.metric(
        "AI service cost",
        f"${ai_result.ai_service_cost:,.2f}",
        help=(
            "Cost of using the AI service for AI assisted cases. "
            "Calculated from AI assisted cases multiplied by AI cost per assisted case."
        ),
    )

    st.metric(
        "AI rework cost",
        f"${ai_result.ai_rework_cost:,.2f}",
        help=(
            "Human labor cost caused by AI errors that require rework. "
            "This cost is already included within Human cost and should not be added again."
        ),
    )

    st.caption(
        "AI rework cost is shown separately for visibility, but it is already included "
        "within Human cost."
    )


with st.expander("How the value calculation works"):
    st.markdown("**Current inputs and calculation**")
    for line in calculation_example(baseline_inputs, ai_inputs, baseline, ai_result):
        st.write(line)
    st.caption("Expected case counts can be fractional. Displayed values are rounded; "
               "the engine calculates with full precision.")
    st.markdown(
        "Baseline cost = direct labor + baseline rework. AI cost = remaining human work "
        "(including review and rework) + AI service cost.\n\n"
        "Adopted direct handling time is floored at zero. Non-adopted cases retain baseline rework. "
        "Monthly savings = baseline cost − AI cost; annual savings = monthly savings × 12.\n\n"
        "Payback = implementation cost / monthly savings **before assurance**; "
        "there is no payback when savings are non-positive. "
        "A positive result does not establish deployment readiness."
    )

st.markdown(f"**Economic signal: {economic_signal(ai_result.monthly_savings)}**")
st.write(economic_inference(ai_result.monthly_savings))
st.caption("Step 1 uses savings before assurance. The Assessment Summary uses monthly value "
           "after assurance, matching the formal decision input. Marginal means exact break-even; "
           "no tolerance band or score is added.")

st.subheader("Automation scope")
automation = automation_scope(adoption_rate, review_rate)
st.write(f"**AI assisted share:** {automation['AI assisted share']:.0%} of monthly cases · "
         f"**Human retained share:** {automation['Human retained share']:.0%} without AI assistance · "
         f"**Human review rate:** {automation['Human review rate']:.0%} of AI-assisted cases")
st.caption("Configured assumptions, not a validated review requirement. AI assistance is not "
           "autonomous automation; assisted cases still include human work. "
           "Human retained share counts cases without AI, not all remaining human effort.")

st.header("2. Reality and risk", anchor="reality-risk")
st.write("Does the AI behave reliably enough in practice, and what AI-related exposure exists?")
st.markdown(f"**Selected HR case category: {case_category}**")
st.caption("Changing the case category updates the AI risk context. Economic assumptions remain "
           "based on the current workflow inputs until you change them.")
st.caption("Synthetic prototype assumptions: all shipped likelihood and impact ratings. "
           "Inherent exposure is derived from these assumptions, not measured HR performance.")
risk_rows = [
    {
        "Dimension": risk.name,
        "Likelihood": risk.likelihood,
        "Impact": risk.impact,
        "Inherent exposure": risk.inherent_exposure,
    }
    for risk in ai_output_risks
]

st.dataframe(
    risk_rows,
    width="stretch",
    hide_index=True,
)

with st.expander("Risk rationales and exposure method"):
    for risk in ai_output_risks:
        st.markdown(f"**{risk.name}:** {risk.description}")
    st.caption("Low=1, Medium=2, High=3. Likelihood × impact: 1–2 Low, 3–4 Medium, "
               "5–9 High. This ordinal screening rubric is not precise quantitative risk.")


with st.expander("Reliability — supporting concepts", expanded=True):
    st.markdown(
        "- **Reliability**\n"
        "  - **Accuracy:** Is the guidance correct and supported?\n"
        "  - **Consistency:** Do materially equivalent queries receive compatible answers?\n"
        "  - **Repeatability:** Do repeated runs remain dependable?\n"
        "  - **Robustness:** Does performance hold under ambiguity and input variation?"
    )
    st.caption("Supporting concepts only; no separate exposure scores. "
               "No HR evaluation results are preloaded. Use scoped evidence below.")

scope = st.text_input(
    "Assessment scope", value=f"{case_category}; illustrative monthly HR workflow",
    key=f"scope:{case_category}",
    help="Specify population, policy/model versions, period and workflow boundary.",
)
st.caption("Changing category or scope starts separate evidence/control declarations. "
           "Economic inputs stay unchanged. After changing costs or workflow assumptions, "
           "review whether evidence still applies; references are not automatically verified.")
prefix = f"{case_category}:{scope}"
factors = {}
with st.expander("Evidence declarations — defaults are Missing"):
    st.caption("Declare only evidence you can substantiate for this scope. "
               "Observations on synthetic fixtures are Synthetic, not representative HR evidence. "
               "Adequacy is a reviewer judgment, not an automated check.")
    for name in FACTOR_NAMES:
        label = name.replace("_", " ").capitalize().replace("Sme", "SME")
        st.markdown(f"**{label}**")
        st.caption({
            "observed_data": "Workflow observations, including effort, rework and control costs.",
            "evaluation_coverage": "Defined evaluation criteria covering all four risk dimensions.",
            "representative_scenarios": "Justified populations, policy contexts and exception cases.",
            "repeat_testing": "Repeated and varied queries under documented model/policy versions.",
            "sme_validation": "Named domain-expert review, including unresolved disagreements.",
            "control_evidence": "Observed implementation and effectiveness of required controls.",
        }[name])
        factors[name] = evidence_fields(label, f"{prefix}:factor:{name}")

evidence = None
if all(factor is not None for factor in factors.values()):
    try:
        evidence = EvidenceAssessment(scope, **factors)
    except (ValueError, TypeError) as exc:
        st.error(f"Assessment evidence: {exc}")

confidence_slot = st.container()
with confidence_slot:
    st.subheader("Evidence and confidence")
    st.info("Risk exposure describes potential harm. Confidence describes the strength of "
            "the supporting evidence. High confidence does not mean Low risk.")
    if evidence is None:
        st.warning("Confidence unavailable: correct the evidence inputs above. "
                   "No previous confidence or recommendation is retained.")
    else:
        confidence = classify_confidence(evidence)
        left, right = st.columns(2)
        left.metric("Evidence maturity", confidence.maturity)
        right.metric("Assessment confidence", confidence.level)
        st.write(confidence.reasons[0])
        with st.expander("Evidence available and confidence rationale"):
            st.caption("Software tests and synthetic profiles are available methodology artifacts; "
                       "they do not validate HR behavior. References below are user declarations.")
            show_lines(confidence.reasons[1:])
        with st.expander("Evidence gaps"):
            if confidence.gaps:
                show_lines(confidence.gaps)
            else:
                st.write("No factor gaps declared. Referenced artifacts still require human review.")

exposures = tuple(risk.inherent_exposure for risk in ai_output_risks)
st.markdown(f"**Risk signal: {highest_exposure(exposures)} — highest inherent exposure**")
if evidence is not None:
    st.write(risk_inference(exposures, confidence.level, confidence.maturity))
else:
    st.write("Confidence and evidence maturity are unavailable until invalid declarations are corrected.")

st.header("3. Assurance and decision", anchor="assurance-decision")
recommendation_slot = st.container()
st.write("What controls are required, what risk remains, how strong is the evidence, "
         "and what deployment posture is justified?")
st.subheader("Applicable controls")
st.caption("A control proposal does not reduce risk. Observed effectiveness requires "
           "evidenced implementation; numeric economic effectiveness is a separate Assumed input.")
controls = []
controls_valid = True
if case_category == "Payroll inquiry":
    st.caption("Illustrative Payroll proposals. Defaults: not implemented, evidence Missing, "
               "effectiveness Assumed. These controls are not operated by this app.")
    for index, proposal in enumerate(PAYROLL_CONTROLS):
        with st.expander(f"{proposal.name} · {proposal.dimension}"):
            st.write(proposal.purpose)
            st.caption(f"Residual concern: {proposal.residual_rationale}")
            implemented = st.checkbox("Implemented", key=f"{prefix}:control:{index}:implemented")
            effectiveness = st.selectbox(
                "Effectiveness status", [s.value for s in EffectivenessStatus], index=1,
                key=f"{prefix}:control:{index}:effectiveness",
            )
            control_evidence = evidence_fields(
                proposal.name, f"{prefix}:control:{index}:evidence",
            )
            if control_evidence is None:
                controls_valid = False
            else:
                try:
                    controls.append(replace(
                        proposal, implemented=implemented, evidence=control_evidence,
                        effectiveness=EffectivenessStatus(effectiveness),
                    ))
                except (ValueError, TypeError) as exc:
                    controls_valid = False
                    st.error(f"{proposal.name}: {exc}")
    if controls_valid:
        st.dataframe([
            {"Control": c.name, "Dimension": c.dimension,
             "Implementation": "Declared implemented" if c.implemented else "Proposed",
             "Evidence": c.evidence.status.value, "Effectiveness": c.effectiveness.value}
            for c in controls
        ], hide_index=True, width="stretch")
else:
    st.info("No category-specific controls have been defined for this HR category. "
            "Payroll proposals are not automatically applied. Control coverage remains a gap.")

st.subheader("Residual review")
st.caption("Without an observed review, the framework retains inherent exposure as an "
           "unverified planning value. Controls alone cannot earn reduction credit.")
reviews = []
reviews_valid = True
for risk in ai_output_risks:
    with st.expander(f"{risk.name} — optional observed residual review"):
        has_review = st.checkbox(
            "Provide an observed residual review", key=f"{prefix}:residual:{risk.name}:enabled",
        )
        if has_review:
            key = f"{prefix}:residual:{risk.name}"
            likelihood = st.selectbox("Residual likelihood", ["Low", "Medium", "High"],
                                      index=["Low", "Medium", "High"].index(risk.likelihood),
                                      key=f"{key}:likelihood")
            impact = st.selectbox("Residual impact", ["Low", "Medium", "High"],
                                  index=["Low", "Medium", "High"].index(risk.impact),
                                  key=f"{key}:impact")
            rationale = st.text_area("Residual rationale", key=f"{key}:rationale")
            reviewer = st.text_input("Reviewer", key=f"{key}:reviewer")
            review_evidence = evidence_fields(f"{risk.name} residual", f"{key}:evidence")
            if review_evidence is None:
                reviews_valid = False
            else:
                try:
                    reviews.append(ResidualReview(
                        risk.category, likelihood, impact, rationale, reviewer, review_evidence,
                    ))
                except (ValueError, TypeError) as exc:
                    reviews_valid = False
                    st.error(f"{risk.name} review: {exc}")

assurance_column, assurance_summary_column = st.columns(2, gap="large")
with assurance_column:
    st.subheader("Assurance economics — Assumed")
    st.caption("Derived from the sidebar assumptions. This calculation does not measure control "
               "effectiveness or reduce the four risk dimensions.")
    with st.expander("How the assurance calculation works"):
        st.markdown(
            f"""
    **You provide two assurance assumptions:**

    **Expected control effectiveness = {control_effectiveness:.0%}**

    This means we are assuming the control prevents this percentage of modeled AI errors.

    **Estimated monthly control cost = ${control_cost:,.2f}**

    This is the assumed monthly cost of operating the control.

    The model then calculates:

    **AI error cases**

    {ai_result.adopted_cases:,.0f} AI assisted cases × {ai_error_rate:.0%} AI rework rate

    = **{ai_result.ai_rework_cases:,.0f} error cases**

    **Errors prevented**

    {ai_result.ai_rework_cases:,.0f} error cases × {control_effectiveness:.0%} control effectiveness

    = **{assurance_result.prevented_error_cases:,.0f} prevented errors**

    **Residual errors**

    {ai_result.ai_rework_cases:,.0f} original errors − {assurance_result.prevented_error_cases:,.0f} prevented errors

    = **{assurance_result.remaining_error_cases:,.0f} residual errors**

    **Original AI rework cost**

    {ai_result.ai_rework_cases:,.0f} errors × {ai_rework_minutes:.1f} minutes / 60 × ${hourly_cost:,.2f}/hour

    = **${ai_result.ai_rework_cost:,.2f}**

    **Avoided rework cost**

    {assurance_result.prevented_error_cases:,.0f} prevented errors × {ai_rework_minutes:.1f} minutes / 60 × ${hourly_cost:,.2f}/hour

    = **${assurance_result.avoided_rework_cost:,.2f}**

    **Residual rework cost**

    {assurance_result.remaining_error_cases:,.0f} residual errors × {ai_rework_minutes:.1f} minutes / 60 × ${hourly_cost:,.2f}/hour

    = **${assurance_result.remaining_rework_cost:,.2f}**

    **Net assurance value**

    ${assurance_result.avoided_rework_cost:,.2f} avoided rework cost − ${assurance_result.control_cost:,.2f} control cost

    = **${assurance_result.net_assurance_value:,.2f}**

    The control effectiveness and control cost are currently user supplied assumptions for experimentation. In a real implementation, they should be supported by evidence such as testing, evaluation results, production monitoring, audit findings, or actual operating costs.

    Net assurance value represents only the direct economic effect modeled here. It does not attempt to convert safety, privacy, fairness, security, compliance, transparency, human oversight, or reliability risk into dollars.
    """
        )

    for row in (
        (("Errors prevented", f"{assurance_result.prevented_error_cases:,.0f}", "errors_prevented"),
         ("Residual errors", f"{assurance_result.remaining_error_cases:,.0f}", "residual_errors"),
         ("Assumed control effectiveness", f"{control_effectiveness:.0%}", "control_effectiveness")),
        (("Avoided rework cost", f"${assurance_result.avoided_rework_cost:,.2f}", "avoided_rework_cost"),
         ("Residual rework cost", f"${assurance_result.remaining_rework_cost:,.2f}", "residual_rework_cost"),
         ("Control cost", f"${assurance_result.control_cost:,.2f}", "control_cost")),
        (("Net assurance value", f"${assurance_result.net_assurance_value:,.2f}", "net_assurance_value"),
         ("Monthly value after assurance", f"${monthly_value_after_assurance:,.2f}",
          "monthly_value_after_assurance")),
    ):
        for label, value, help_key in row:
            st.metric(label, value, help=HELP_TEXT[help_key])
    if assurance_result.net_assurance_value > 0:
        st.success(
            "The assurance control creates positive economic value under these assumptions. "
            "The avoided AI rework cost is greater than the cost of the control."
        )
    elif assurance_result.net_assurance_value == 0:
        st.info(
            "The assurance control is at break even under these assumptions."
        )
    else:
        st.warning(
            "The assurance control costs more than the AI rework cost it currently avoids. "
            "This does not automatically mean the control should be removed because safety, "
            "privacy, compliance, and other responsible AI risks may have value beyond direct rework cost."
        )


with st.expander("Decision inputs and unresolved gaps"):
    st.caption("Record one gap per line. Critical gaps are known blockers, not simply missing data. "
               "Clear a gap only after reviewing supporting evidence for this scope.")
    unresolved = st.text_area(
        "Unresolved gaps", value="Full control cost and review effort are unobserved.",
        key=f"{prefix}:gaps",
    )
    critical = st.text_area("Critical gaps", key=f"{prefix}:critical")

decision = None
with recommendation_slot:
    st.subheader("Deployment recommendation")
    st.caption("Advisory result within the stated scope; not deployment authorization. "
               "Observed labels below reflect supplied declarations, not app-verified artifacts.")
    if evidence is None or not controls_valid or not reviews_valid:
        st.error("Recommendation unavailable: correct invalid evidence, control or residual inputs. "
                 "No previous recommendation is retained.")
    else:
        try:
            decision = recommend_deployment(
                monthly_value=monthly_value_after_assurance, evidence=evidence,
                risks=ai_output_risks, controls=tuple(controls), reviews=tuple(reviews),
                unresolved_gaps=tuple(line.strip() for line in unresolved.splitlines() if line.strip()),
                critical_gaps=tuple(line.strip() for line in critical.splitlines() if line.strip()),
            )
        except (ValueError, TypeError) as exc:
            st.error(f"Recommendation unavailable: {exc}")
        else:
            st.markdown(f"**Decision signal: {decision_signal(decision.posture)}**")
            st.caption("Formal deployment posture")
            st.markdown(f"### {decision.posture}")
            st.caption(f"Assessment confidence: {decision.confidence.level} · "
                       f"Evidence maturity: {decision.confidence.maturity}")
            st.markdown("**Decision scope**")
            st.write(decision_scope(decision.posture, adoption_rate, review_rate))
            st.markdown("**Why**")
            st.write(decision.reasons[0])
            can_proceed, retained = scope_actions(decision.posture)
            st.markdown("**What can proceed now**")
            st.write(can_proceed)
            st.markdown("**What should remain human reviewed or restricted**")
            st.write(retained)
            st.markdown("**Next action**")
            st.write(next_action(decision.posture))

with assurance_summary_column:
    st.subheader("Controls and residual risk summary")
    if decision is None:
        st.warning("Correct invalid declarations to obtain a residual assessment. "
                   "No previous summary is retained.")
    else:
        if not controls:
            st.caption("No category-specific controls supplied; coverage remains a gap.")
        for residual in decision.residual_risks:
            with st.container(border=True):
                st.markdown(f"**{residual.dimension} · Residual exposure: {residual.exposure}**")
                st.caption("Observed review declared" if residual.evidence_supported
                           else "Unverified carry-forward; no observed residual review")
                applicable = [c for c in controls if c.dimension == residual.dimension]
                for control in applicable:
                    st.write(f"{control.name}: evidence {control.evidence.status.value}; "
                             f"effectiveness {control.effectiveness.value}.")
                if not applicable:
                    st.write("No applicable control supplied.")

if decision is not None:
    st.markdown("**Residual risks**")
    st.dataframe([
        {"Dimension": r.dimension, "Inherent": r.inherent_exposure, "Residual": r.exposure,
         "Status": "Evidence-supported declaration" if r.evidence_supported
         else "Unverified carry-forward"}
        for r in decision.residual_risks
    ], hide_index=True, width="stretch")
    with st.expander("Residual risk rationale"):
        for residual in decision.residual_risks:
            st.markdown(f"**{residual.dimension}:** {residual.rationale}")
    with st.expander("Why this recommendation"):
        show_lines(decision.reasons)
    with st.expander("Required controls"):
        if decision.required_controls:
            show_lines(decision.required_controls)
        else:
            st.write("No controls supplied. This does not establish that controls are unnecessary; "
                     "see coverage gaps below.")
    with st.expander("Recommendation evidence gaps"):
        show_lines(decision.evidence_gaps)
        if not decision.evidence_gaps:
            st.write("No gaps declared; human review remains required.")
    with st.expander("What would change the decision"):
        show_lines(decision.what_would_change)

with st.expander("Deployment posture definitions"):
    st.markdown(
        "- **Proceed:** positive value, High confidence, supported Low residuals and no open gaps.\n"
        "- **Proceed with controls:** proceed only within the evidenced controlled scope.\n"
        "- **Pilot and gather evidence:** propose a separately approved, bounded evaluation.\n"
        "- **Restricted deployment:** a known constraint blocks broad use; narrower use needs review.\n"
        "- **Insufficient evidence:** no supported deployment conclusion is available."
    )
    st.caption("Ordered rules are implemented in the assessment modules. A critical gap, "
               "evidenced High residual or non-positive value outranks missing evidence.")
st.markdown("[Back to Value](#value) · [Back to Reality and risk](#reality-risk)")

# Fill the top summary only from this rerun's outputs, never cached prior recommendations.
with summary_slot:
    st.subheader("Assessment Summary")
    signal = decision_signal(decision.posture) if decision is not None else "Unavailable"
    cards = (
        ("Value", economic_signal(monthly_value_after_assurance), "After assumed assurance"),
        ("Risk", highest_exposure(exposures), "Highest inherent exposure · Synthetic"),
        ("Confidence", confidence.level if evidence is not None else "Unavailable",
         "Support for this assessment"),
        ("Decision signal", signal, decision.posture if decision is not None
         else "Correct invalid assessment inputs"),
    )
    st.markdown(
        '<div class="assessment-summary">' + ''.join(
            f'<div class="summary-card"><span class="summary-label">{escape(label)}</span>'
            f'<strong>{escape(value)}</strong><span class="summary-note">{escape(note)}</span></div>'
            for label, value, note in cards
        ) + '</div>', unsafe_allow_html=True,
    )
    if decision is not None:
        st.subheader("Executive readout")
        st.write(executive_readout(
            case_category, monthly_value_after_assurance, ai_inputs, exposures,
            decision.confidence.level, decision.confidence.maturity, decision.posture,
        ))
    else:
        st.warning("Assessment incomplete: correct invalid declarations below. "
                   "No previous decision signal is retained.")

    st.markdown("**Current configuration**")
    configuration = configuration_summary(
        case_category, baseline_inputs, ai_inputs, assurance_inputs,
        confidence.maturity if evidence is not None else "Unavailable — invalid declarations",
    )
    st.caption(" · ".join(f"{label}: {value}" for label, value in configuration.items()))
    st.caption("Case category changes risk context, not economics. "
               "Economic figures use the workflow assumptions currently configured.")

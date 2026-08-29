import streamlit as st

from ai_value_lab import (
    AIInputs,
    AssuranceInputs,
    BaselineInputs,
    Risk,
    calculate_ai_scenario,
    calculate_assurance,
    calculate_baseline,
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
st.set_page_config(page_title="AI Value Lab", page_icon="📊", layout="wide")

st.title("AI Value Lab")

st.markdown("### Reference use case: AI assisted employee HR case handling")

st.caption(
    "This lab models an enterprise HR service workflow where AI assists with "
    "eligible employee cases while economic value and Responsible AI exposure "
    "are assessed separately."
)

st.info(
    "**Current scope:** AI can retrieve information, summarize information, "
    "and draft responses for HR policy, benefits, employee data, and payroll inquiries. "
    "It does not autonomously change payroll, modify employee records, approve benefits, "
    "or make employment decisions.\n\n"
    "**Phase 1:** All values are synthetic assumptions unless explicitly supported by evidence. "
    "No model API, Claude account, or API key is required."
)

with st.sidebar:
    st.header("Current workflow")

    st.subheader("Risk context")
    case_category = st.selectbox(
        "Case category for risk assessment",
        [
            "General HR policy",
            "Benefits",
            "Employee data",
            "Payroll inquiry",
        ],
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

    st.header("AI assurance")
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

ai_output_risk = Risk(
    name="Incorrect AI output",
    category="Reliability",
    description="AI assisted cases may produce incorrect or unusable output.",
    likelihood="Medium",
    impact="Medium",
)

baseline = calculate_baseline(baseline_inputs)
ai_result = calculate_ai_scenario(baseline_inputs, ai_inputs)
assurance_result = calculate_assurance(ai_result, assurance_inputs)

monthly_value_after_assurance = (
    ai_result.monthly_savings + assurance_result.net_assurance_value
)

st.subheader("Economic comparison")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Current monthly cost",
    f"${baseline.total_monthly_cost:,.0f}",
)

col2.metric(
    "AI enabled monthly cost",
    f"${ai_result.total_monthly_cost:,.0f}",
)

col3.metric(
    "Monthly value before assurance",
    f"${ai_result.monthly_savings:,.0f}",
    help=HELP_TEXT["monthly_value_before_assurance"],
)

col4.metric(
    "Monthly value after assurance",
    f"${monthly_value_after_assurance:,.0f}",
    help=HELP_TEXT["monthly_value_after_assurance"],
)

col5, col6, col7 = st.columns(3)

col5.metric(
    "Current cost per case",
    f"${baseline.cost_per_case:,.2f}",
)

col6.metric(
    "AI enabled cost per case",
    f"${ai_result.cost_per_case:,.2f}",
)

col7.metric(
    "Payback",
    "No payback"
    if ai_result.payback_months is None
    else f"{ai_result.payback_months:,.1f} months",
    help=HELP_TEXT["payback"],
)

st.subheader("What is driving the AI result?")

st.write(
    {
        "AI assisted cases": round(ai_result.adopted_cases),
        "AI error cases": round(ai_result.ai_rework_cases),
        "Remaining human hours": round(ai_result.human_hours, 1),
        "Human cost": round(ai_result.human_cost, 2),
        "AI service cost": round(ai_result.ai_service_cost, 2),
        "AI rework cost": round(ai_result.ai_rework_cost, 2),
    }
)

st.subheader("AI assurance")

st.markdown("#### Risk profile")

risk_col1, risk_col2, risk_col3 = st.columns(3)

risk_col1.metric(
    "Risk",
    ai_output_risk.name,
)

risk_col2.metric(
    "Category",
    ai_output_risk.category,
)

risk_col3.metric(
    "Inherent exposure",
    ai_output_risk.inherent_exposure,
)

likelihood_col, impact_col = st.columns(2)

likelihood_col.metric(
    "Likelihood",
    ai_output_risk.likelihood,
)

impact_col.metric(
    "Impact",
    ai_output_risk.impact,
)

st.caption(ai_output_risk.description)

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

{ai_result.ai_rework_cases:,.0f} errors × {ai_rework_minutes:.1f} minutes × ${hourly_cost:,.2f}/hour  
= **${ai_result.ai_rework_cost:,.2f}**

**Avoided rework cost**

{assurance_result.prevented_error_cases:,.0f} prevented errors × {ai_rework_minutes:.1f} minutes × ${hourly_cost:,.2f}/hour  
= **${assurance_result.avoided_rework_cost:,.2f}**

**Residual rework cost**

{assurance_result.remaining_error_cases:,.0f} residual errors × {ai_rework_minutes:.1f} minutes × ${hourly_cost:,.2f}/hour  
= **${assurance_result.remaining_rework_cost:,.2f}**

**Net assurance value**

${assurance_result.avoided_rework_cost:,.2f} avoided rework cost − ${assurance_result.control_cost:,.2f} control cost  
= **${assurance_result.net_assurance_value:,.2f}**

The control effectiveness and control cost are currently user supplied assumptions for experimentation. In a real implementation, they should be supported by evidence such as testing, evaluation results, production monitoring, audit findings, or actual operating costs.

Net assurance value represents only the direct economic effect modeled here. It does not attempt to convert safety, privacy, fairness, security, compliance, transparency, human oversight, or reliability risk into dollars.
"""
    )
col8, col9, col10, col11 = st.columns(4)

col8.metric(
    "AI error cases",
    f"{ai_result.ai_rework_cases:,.0f}",
    help=HELP_TEXT["ai_error_cases"],
)

col9.metric(
    "Errors prevented",
    f"{assurance_result.prevented_error_cases:,.0f}",
    help=HELP_TEXT["errors_prevented"],
)

col10.metric(
    "Residual errors",
    f"{assurance_result.remaining_error_cases:,.0f}",
    help=HELP_TEXT["residual_errors"],
)

col11.metric(
    "Control effectiveness",
    f"{control_effectiveness:.0%}",
    help=HELP_TEXT["control_effectiveness"],
)

col12, col13, col14, col15 = st.columns(4)

col12.metric(
    "Original AI rework cost",
    f"${ai_result.ai_rework_cost:,.2f}",
    help=HELP_TEXT["original_ai_rework_cost"],
)

col13.metric(
    "Avoided rework cost",
    f"${assurance_result.avoided_rework_cost:,.2f}",
    help=HELP_TEXT["avoided_rework_cost"],
)

col14.metric(
    "Residual rework cost",
    f"${assurance_result.remaining_rework_cost:,.2f}",
    help=HELP_TEXT["residual_rework_cost"],
)

col15.metric(
    "Control cost",
    f"${assurance_result.control_cost:,.2f}",
    help=HELP_TEXT["control_cost"],
)

st.metric(
    "Net assurance value",
    f"${assurance_result.net_assurance_value:,.2f}",
    help=HELP_TEXT["net_assurance_value"],
)

st.subheader("Interpretation")

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

st.caption(
    "The next phase expands assurance from operational AI errors into specific responsible AI risks, controls, residual risk, and business impact."
)

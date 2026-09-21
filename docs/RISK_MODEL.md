# AI Value Lab risk model

**Status: all current HR profile likelihood and impact ratings are synthetic
prototype assumptions.** They are authored scenario judgments, not measured
failure probabilities, validated impact estimates, or deployment approvals.
Inherent exposure is derived from those assumptions and is not new evidence.

## Three-part assessment

1. **AI Value Assessment:** determine whether the use case creates economic value
   under the supplied assumptions. The existing baseline, AI workflow, and
   assurance economics remain unchanged.
2. **Reality and Risk Assessment:** assess AI-related Reliability, Privacy,
   Compliance, and Operational Impact separately from economic value.
3. **Assurance and Decision:** connect evidence, controls, residual risk,
   confidence, and a deployment recommendation. Dedicated V1 modules implement
   transparent advisory rules; they are not yet connected to the Streamlit UI.

The full reasoning chain is Value → Reality → Risk → Evidence → Controls →
Residual Risk → Confidence → Decision. See [assessment rules](ASSESSMENT_METHOD.md)
and the [Payroll Inquiry assessment](PAYROLL_ASSESSMENT.md).

## AI-related risk scope

The Streamlit reference workflow assists with retrieving information, summarizing
information, and drafting responses for General HR policy, Benefits, Employee
data, and Payroll inquiry cases. It does not autonomously change payroll, modify
employee records, approve benefits, or make employment decisions.

Assess failures introduced or amplified by AI assistance within that workflow.
This is not a comprehensive enterprise risk register. The selected category
changes the risk context; economic calculations still cover the full monthly
workflow. Risk labels do not modify economic inputs or outputs.

## The four dimensions

| Dimension | Meaning in this prototype |
| --- | --- |
| Reliability | Whether AI output can be depended on for the intended HR task; failures include incorrect, incomplete, or inconsistent guidance. |
| Privacy | Exposure from AI processing or disclosing employee, dependent, health, personal, or financial information inappropriately. |
| Compliance | Exposure from AI guidance or data handling conflicting with applicable requirements or internal policy; these profiles do not determine legal compliance. |
| Operational Impact | Disruption caused by AI failures, including confusion, escalations, urgent corrections, downstream process errors, and remediation effort. |

Accuracy (correctness), Consistency (agreement across equivalent inputs),
Repeatability (stability across repeated runs), and Robustness (performance under
input variation or difficult conditions) can support Reliability evidence. They
are not additional top-level risk scores. One failure can affect several
dimensions; the model does not sum the dimensions into an overall risk score.

## Likelihood definitions

These qualitative working definitions explain the prototype labels. They are
not empirically calibrated probability bands. An assessment should specify its
failure event, workflow conditions, unit of exposure, and observation period
before using measured evidence to assign a label.

| Label | Working definition |
| --- | --- |
| Low | The failure is considered uncommon in a bounded workflow and period; the rationale should identify why the failure conditions are unusual. No failures in a small test alone is insufficient. |
| Medium | The failure is plausible in ordinary use, including identifiable exceptions or ambiguous inputs; specify when and how often those conditions arise. |
| High | The failure is expected to recur under common workflow conditions or has recurred in representative observations; identify the exposure and supporting rationale. |

Data sensitivity alone does not establish a failure probability. In particular,
the High privacy likelihood assumptions for employee data and payroll require
validation against actual data flows, access conditions, and failure evidence.

## Impact definitions

Impact describes the consequence if the specified AI-related failure occurs,
not how often it occurs. These are provisional qualitative definitions without
monetary thresholds or jurisdiction-specific criteria.

| Label | Working definition |
| --- | --- |
| Low | Limited, localized consequences that can be corrected with routine effort. |
| Medium | Meaningful employee or process consequences requiring additional handling or escalation. |
| High | Serious employee, sensitive-data, compliance, or operational consequences requiring substantial or urgent remediation. |

## Inherent exposure calculation

The existing `Risk.inherent_exposure` property in
[`models.py`](../src/ai_value_lab/models.py) maps Low to 1, Medium to 2, and High
to 3, then multiplies likelihood by impact:

`score = likelihood_level * impact_level`

- Score 1 to 2: Low exposure.
- Score 3 to 4: Medium exposure.
- Score 5 to 9: High exposure.

Only 1, 2, 3, 4, 6, and 9 are reachable from valid inputs. The High band begins
at 5 conceptually, but its first reachable score is 6. Tests exercise the actual
2/3 and 4/6 transitions without changing the formula or accepting raw scores.

| Likelihood / Impact | Low | Medium | High |
| --- | --- | --- | --- |
| Low | Low | Low | Medium |
| Medium | Low | Medium | High |
| High | Medium | High | High |

This is an ordinal screening convention, not expected financial loss or a
statistically calibrated risk quantity. Inherent means before crediting the
assurance control being assessed; the prototype does not explicitly represent
all existing workflow controls. The unchanged UI displays inherent exposure;
the separate V1 control module supports an evidence-gated residual review.
Invalid likelihood or impact strings raise `ValueError` when
exposure is accessed, not when the dataclass is constructed. Labels are
case-sensitive and must be exactly Low, Medium, or High.

## Current synthetic profile assumptions

Each cell lists **likelihood / impact / derived inherent exposure**. All sixteen
ratings below are prototype assumptions, including those labeled Low.

| HR category | Reliability | Privacy | Compliance | Operational Impact |
| --- | --- | --- | --- | --- |
| General HR policy | Medium / Medium / Medium | Low / Medium / Low | Medium / Medium / Medium | Low / Medium / Low |
| Benefits | Medium / High / High | Medium / High / High | Medium / High / High | Medium / High / High |
| Employee data | Medium / Medium / Medium | High / High / High | High / High / High | Medium / High / High |
| Payroll inquiry | Medium / High / High | High / High / High | High / High / High | High / High / High |

[`risk_profiles.py`](../src/ai_value_lab/risk_profiles.py) supplies the ratings
and scenario rationales. Unknown category strings raise
`ValueError("Unknown case category: ...")`; there is no fallback, whitespace
normalization, or case normalization.

## Assumptions versus evidence

An assumption is an authored or user-supplied estimate without supporting
measurement for the stated context. A rationale explains an assumption but does
not validate it. Evidence is a traceable observation or evaluation with a defined
scope, dataset, method, date, model version, and limitations. A derived value
inherits the limitations of its inputs. Synthetic evaluation data can test a
method, but does not by itself establish real-world HR performance.

The repository also contains a customer-support evaluation runner, grader,
analysis, case set, and policy pack. Their presence does not establish evidence
for these HR profile ratings. The profiles themselves have no attached observed
HR evidence. V1 evidence, control, and decision modules can assess explicitly
supplied records; their existence does not validate the default profiles.

Current assurance economics estimate prevented error cases and avoided rework
cost from a supplied control-effectiveness assumption, then subtract control
cost. Remaining errors and remaining rework cost are economic outputs, not
measured residual Privacy, Compliance, Reliability, or Operational Impact risk.
Positive savings do not establish readiness to deploy.

## Why use this rubric, and how to calibrate it

The small matrix makes assumptions visible, supports consistent discussion, and
helps prioritize investigations without implying a precision the prototype lacks.
Multiplying ranks assumes a convenient ordering, not equal probability or harm
intervals. High is not three times Low. A score of 6 is not twice the real-world
risk of 3. Distinct failure mechanisms can share a cell. Correlated dimensions
must not be added into an overall score. High impact with Low likelihood still
needs explicit review even when the matrix returns Medium.

Before organizational use, owners should:

1. Define the use case boundary, population, jurisdiction, decision authority,
   failure event, exposure unit (for example, per inquiry), and observation period.
2. Agree on anchored examples and acceptable consequences in each dimension;
   set empirical frequency bands only when a defensible denominator exists.
3. Have multiple SMEs independently rate examples and resolve disagreements.
4. Test representative scenarios, edge cases and repeated runs; record failures,
   sample sizes, model/policy versions, and coverage limitations, including zero
   failures with insufficient observations.
5. Reassess likelihood and impact using those records, document changed ratings
   and reviewer reasoning, and separately review decision thresholds and controls.
6. Revalidate after a model, policy, population, jurisdiction, or workflow change.

Domain context can change impact without changing the underlying model behavior.
An incorrect description of a routine pay-code label may cause clarification work;
incorrect advice about an urgent missed payment may affect an employee's ability
to meet essential expenses. Information already public differs from personal
financial data. These are illustrative contrasts, not alternative shipped ratings.
The current HR pairs remain unchanged pending human review.

## Four distinct concepts

| Concept | Meaning | V1 treatment |
| --- | --- | --- |
| Inherent risk | Exposure before crediting the assessed additional controls | Existing likelihood × impact matrix; defaults are synthetic assumptions |
| Residual risk | Exposure remaining with specified controls in a defined scope | No automatic discount; retain inherent exposure as an unverified planning value unless an observed residual review is supplied |
| Evidence maturity | How far evidence has progressed from assumptions to covered, corroborated observations | Categorical descriptor from six evidence factors |
| Confidence | Strength of support for the assessment within its stated scope | Low, Medium, or High, with a rule explanation and gaps; never a percentage |

High confidence can support a finding of High risk. Low confidence does not mean
Low risk. A favorable observed result on synthetic fixtures remains limited to
those fixtures and cannot silently become observed representative HR evidence.

## Methodological decisions requiring human review

- Validate all sixteen likelihood/impact pairs with HR, privacy, compliance,
  and operational owners; agree on concrete failure scenarios and evidence.
- Approve or revise the provisional label definitions, exposure period,
  probability bands, and consequence thresholds before operational use.
- Review multiplying ordinal levels and the existing cutoffs, especially the
  Medium exposure assigned to Low likelihood with High impact. These thresholds
  are preserved, not endorsed as deployment criteria.
- Define which existing controls are included in the inherent-risk baseline,
  how effectiveness is evidenced per dimension, and how residual risk is assessed.
- Define evidence sufficiency, confidence, decision ownership, acceptance limits,
  and deployment gates. Do not infer these from the current economics or labels.

## Regression coverage

[`test_risk_profiles.py`](../tests/test_risk_profiles.py) locks the four categories,
exactly four dimensions in their current display order, all sixteen rating pairs
and exposures, all nine exposure combinations, invalid labels, and unknown
categories. These tests verify implementation consistency, not empirical validity.

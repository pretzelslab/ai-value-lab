# Payroll Inquiry: Value and Assurance Assessment

**Assessment ID:** PAYROLL-V1-ILLUSTRATIVE  
**Status:** Synthetic worked example; not an approved deployment assessment  
**Scope:** AI-assisted payroll inquiry guidance within an illustrative monthly HR workflow  
**Evidence cutoff:** No observed HR evidence supplied  
**Accountable owner / reviewer:** Not assigned; human review required  
**Source:** AI Value Lab package 0.1.0, existing economic defaults and Payroll inquiry profile  
**Format:** Structured Markdown assessment source for later Word/PDF conversion

## Use case summary

An AI assistant retrieves approved information, summarizes payroll policy and
drafts responses for a payroll professional. It does not update payroll, modify
employee records, authorize deductions or make employment decisions. Any downstream
action remains a human responsibility. These are **illustrative scope constraints**,
not implemented access controls in this toolkit.

Value → Reality → Risk → Evidence → Controls → Residual Risk → Confidence → Decision

The model shows an economically promising scenario but returns **Insufficient
evidence** for deployment. No observed payroll outputs, employee outcomes,
control evaluations or SME approvals are represented in this assessment.

## 1. Value assessment

### Economic assumptions

Every input in this table is **Assumed / Synthetic**, including the costs and
effectiveness of assurance. USD is an illustrative reporting currency.

| Input | Assumed value |
| --- | ---: |
| Monthly workflow cases | 10,000 |
| Baseline minutes per case | 10 |
| Loaded hourly labor cost | $45 |
| Baseline rework rate | 8% |
| Baseline minutes per rework | 6 |
| AI adoption rate | 70% |
| Minutes saved per adopted case before review/rework | 6 |
| Human review rate | 30% |
| Minutes per review | 2 |
| AI service cost per adopted case | $0.08 |
| AI error/rework rate | 6% |
| Minutes per AI rework | 6 |
| One-time implementation cost | $50,000 |
| Assurance control effectiveness for modeled rework | 75% |
| Monthly assurance control cost | $1,000 |

These are the existing full-workflow defaults, not payroll-specific measured
volumes or unit costs. Selecting Payroll inquiry supplies risk context only.
Do not extrapolate the resulting savings to an actual payroll function.

### Economic value

All results below are **derived from Assumed / Synthetic inputs**, not observed
savings. Formulas are unchanged in `value_model.py`; the app's post-assurance
value is AI monthly savings plus net assurance value.

| Result | Conditional model output |
| --- | ---: |
| Baseline monthly cost | $78,600 |
| AI-assisted cases | 7,000 |
| AI workflow monthly cost, before assurance | $50,180 |
| Baseline / AI cost per case | $7.86 / $5.018 |
| Monthly savings before assurance | $28,420 |
| Annual savings before assurance | $341,040 |
| Simple payback before assurance | About 1.76 months |
| AI errors requiring rework before assurance | 420 cases/month |
| AI rework cost before assurance | $1,890/month |
| Errors prevented under assumed assurance | 315 cases/month |
| Remaining modeled errors | 105 cases/month |
| Avoided / remaining rework cost | $1,417.50 / $472.50 per month |
| Net assurance value | $417.50/month |
| Monthly value after assumed assurance | $28,837.50 |

The dollar precision makes arithmetic reproducible; it is not empirical precision.
Payback excludes assurance and uses $50,000 / $28,420. Annual savings multiply
monthly savings by twelve; they are not a realized first-year return after all
implementation expenditure. No privacy/compliance harm is monetized.

The assumed 30% review and $1,000 control cost do **not** establish the review
coverage or full cost of the four proposed controls below. In particular, C4 may
require human authorization for every consequential action. Its actual effort
and the cost of C1-C3 must be observed and the economic inputs reassessed before
deployment. The illustrative financial benefit is conditional on that open gap.

## 2. Reality and risk assessment

### Reality check

There is no HR AI execution in this example. Accuracy, Consistency, Repeatability
and Robustness are **not measured**. They support one Reliability dimension.
No synthetic response is presented as an actual system response or incident.

### Four-dimension risk profile

Likelihood and impact are **Synthetic prototype assumptions**. Inherent exposure
is **derived from those assumptions**, using Low=1, Medium=2, High=3 and the existing
1-2 Low, 3-4 Medium, 5-9 High exposure thresholds.

| Dimension | Assumed likelihood | Assumed impact | Derived inherent exposure |
| --- | --- | --- | --- |
| Reliability | Medium | High | High (2 × 3 = 6) |
| Privacy | High | High | High (3 × 3 = 9) |
| Compliance | High | High | High (3 × 3 = 9) |
| Operational Impact | High | High | High (3 × 3 = 9) |

These are the shipped ratings, unchanged. Sensitivity of payroll data alone does
not validate High likelihood; frequency and consequences require separate evidence.

### Illustrative failure modes and traceability

All six scenarios below are **Illustrative**, not observed failures. Primary
dimensions organize review without implying that consequences cannot overlap.

| ID | Failure mode | Primary dimension / supporting concept | Proposed control | Evidence needed |
| --- | --- | --- | --- | --- |
| F1 | Incorrect explanation of a deduction misleads an employee | Reliability / Accuracy | C1 | SME-labeled payroll answers, source checks, error and severity analysis |
| F2 | An answer reveals another employee's payroll information | Privacy | C2 | Authorized access and disclosure tests, including unauthorized recipient cases |
| F3 | Guidance uses a policy for the wrong jurisdiction or effective date | Compliance | C3 | Versioned policy mapping and SME-reviewed jurisdiction/date test cases |
| F4 | Materially equivalent questions receive contradictory answers | Reliability / Consistency, Repeatability | C1 | Equivalent-query pairs and repeated runs under a fixed version |
| F5 | A confident answer invents support for an ambiguous payroll claim | Reliability / Accuracy, Robustness | C1 and C3 | Ambiguous/perturbed cases, source validity and escalation checks |
| F6 | A human acts on incorrect guidance and triggers an inappropriate payroll correction | Operational Impact | C4 | Sandbox action-gate, handoff and escalation drills, including incorrect-advice scenarios |

F6 is a downstream consequence of advice; it does not imply the assistant can
autonomously change payroll. F2/F3 can also cause operational disruption. The
dimensions are not summed, and failure counts must avoid double-counting events.

## 3. Evidence available and gaps

Available artifacts: deterministic formulas, unit tests, synthetic profile
rationales, the risk methodology, and the existing separate support evaluation
tooling. These establish software behavior and a method; they do not establish
HR AI performance or control effectiveness. No support dry-run result is credited.

| Evidence factor | Current assessment status | Gap |
| --- | --- | --- |
| Observed workflow data | Missing; economics are Assumed | Representative handling time, rework, case volumes and full control costs |
| Evaluation coverage | Missing | Scoped tests across all four dimensions and F1-F6 with pre-agreed criteria |
| Representative scenarios | Missing | Population, language, policy, jurisdiction, routine and exception case mix |
| Repeat testing | Missing | Repeated and equivalent/perturbed inquiries with fixed versions |
| SME validation | Missing | Named payroll/domain review and disagreement resolution |
| Control evidence | Missing | Implementation and effectiveness observations for C1-C4 |

No sample size, measured success rate, confidence percentage or sign-off is invented.
An assessment owner must define adequacy criteria before collecting evidence.

## 4. Controls

These are the **Illustrative proposed** `PAYROLL_CONTROLS` in `controls.py`.
All are required proposals for this assessment, with `implemented=False`, evidence
status **Missing**, and effectiveness status **Assumed**. They do not inherit the
economic model's 75% effectiveness; each must be evaluated on its own failure modes.

| Control | Purpose and dimension | Residual risk rationale |
| --- | --- | --- |
| C1 Source-grounded review | Reliability: compare drafts to approved sources; escalate unsupported answers; examine equivalent queries | Plausible errors may survive review; repeated and robustness tests remain necessary |
| C2 Data minimization and access checks | Privacy: restrict fields and validate recipient access | Redaction and authorization may fail; leakage and access evidence is absent |
| C3 Policy and jurisdiction review | Compliance: use versioned sources and SME escalation | Approved sources may still be stale or misapplied; legal compliance is not established |
| C4 Human action gate | Operational Impact: advisory output only; responsible human authorizes downstream actions and can stop work | Human reviewers can rely on incorrect advice; escalation and handoff behavior are untested |

Control owners, review effort, escalation destinations and acceptance criteria
remain unassigned. The software describes these controls; it does not operate them.

## 5. Residual risk

No observed residual review exists. No reduction is credited for any proposed
control. The model retains inherent exposure as an **unverified Assumed planning
value**, not a measured residual conclusion.

| Dimension | Planning residual exposure | Evidence status | Remaining concern |
| --- | --- | --- | --- |
| Reliability | High | Unverified carry-forward | Incorrect, inconsistent or unsupported guidance |
| Privacy | High | Unverified carry-forward | Unauthorized disclosure of payroll information |
| Compliance | High | Unverified carry-forward | Wrong policy/jurisdiction interpretation |
| Operational Impact | High | Unverified carry-forward | Incorrect human action, urgent corrections and disruption |

The 105 remaining modeled errors are an economic scenario output and do not
quantify any of these four residual risk dimensions.

## 6. Confidence

**Low — No observed evidence.** All six evidence factors are Missing. The core
gate requires adequate observed data, evaluation coverage and representative
scenarios; none is supported. Synthetic assumptions and software tests cannot
meet it. Confidence is support for this assessment, not the probability of safety.

## 7. Illustrative deployment recommendation

**Insufficient evidence.** Positive assumed monthly value does not justify
deployment. The decision model exposes six factor gaps, four unverified required
controls, four unverified residual assessments, and the unresolved full-control-cost
and review-effort gap. No known incident or critical
blocker is asserted; missing evidence is not proof that no blocker exists.

This does not authorize employee-facing payroll use. A sensible next activity is
to design a separately reviewed offline evaluation using authorized, minimized
data and the proposed controls. That planning activity is not a claim that the
model returned Pilot and gather evidence.

### What would change the decision

1. Supply scoped observations for economics and the core evaluation/representative
   coverage factors. With adequate core support but remaining corroboration gaps,
   the rules can return **Pilot and gather evidence**, subject to separate approval.
2. Implement and evaluate C1-C4, perform repeat testing and SME review, and provide
   observed residual reassessments for all dimensions. Recalculate economics from
   the actual control effort and cost.
3. Positive value, High confidence, evidenced controls, supported residuals no higher
   than Medium and no open gaps can support **Proceed with controls** within scope.
4. An observed High residual, a critical blocker or non-positive monthly value
   changes the posture to **Restricted deployment**, even if confidence is High.
5. **Proceed** without required additional controls is not the expected Payroll path;
   the current Medium/High inherent exposure requires applicable controls.

All transitions are **Illustrative rule behavior**, not predictions or approvals.
Changing model, policy, population, workflow or controls triggers reassessment.

## Assumption register and review needs

- All economic quantities are Assumed/Synthetic; exact formulas are reproducible.
- All inherent pairs are Synthetic; the calibration and matrix need owner review.
- F1-F6 and C1-C4 are Illustrative; no incidents or implementations are claimed.
- Residual ratings are unverified carry-forwards; confidence is Low by rule.
- The posture is an Illustrative advisory output, not a legal or operational approval.
- Human owners must approve scope, evidence criteria, control costs, residual
  judgments, critical-gap classification and risk acceptance.

## Reproduction and download source

Use the Python example in the [README](../README.md); it calls the existing
economics, Payroll risk profile and new decision module. The integration test
`test_payroll_worked_example_matches_documented_values_and_posture` pins the main
figures and posture. The Markdown file itself is the assessment source to download
or later convert; no Word/PDF artifact or UI download control exists yet.

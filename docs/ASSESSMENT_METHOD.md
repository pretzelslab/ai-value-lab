# V1 evidence, assurance, and decision rules

**Status: provisional, deterministic assessment conventions for human review.**
These modules are reusable Python logic, not UI features, operational controls,
legal conclusions, or authorization to deploy. No percentages describe confidence.

## Scope and provenance

Define the population, task, model and policy versions, period, workflow, control
boundary, and evidence acceptance criteria in the assessment scope and referenced
records. Evidence factors are reviewer assertions, not automatic artifact checks.
References should identify the author/reviewer, date, method, sample, results,
limitations and version. Do not use these inputs to promote invented evidence.

`EvidenceFactor` has a status, reference and `adequate` flag:

| Status | Meaning | Confidence credit |
| --- | --- | --- |
| Missing | No supporting artifact available | None |
| Assumed | Authored expectation or user-supplied estimate | None |
| Synthetic | Illustrative or fixture-only support; not representative HR observations | None |
| Observed | Actual observations applicable to the named scope, with a reference | Only when a reviewer also attests adequacy |

Observed results from a synthetic test are still useful for engineering, but this
V1 rubric conservatively does not count fixture-only results as representative HR
evidence. Observed data need not be placed in this repository: use safe references
to authorized records. `adequate=True` with any non-Observed status is rejected;
Observed without a reference is rejected. Missing evidence defaults to Missing,
not an optimistic value. References are text, not fetched or authenticated.

## Six evidence factors

| Factor | What adequate support should establish |
| --- | --- |
| `observed_data` | Relevant workflow observations, including time, rework and cost if making a deployment/value claim; scope and provenance documented |
| `evaluation_coverage` | A planned evaluation with defined acceptance criteria covering the four dimensions and relevant failure modes, including adverse outcomes |
| `representative_scenarios` | A justified case mix, populations, jurisdiction/policy contexts and exceptions; exclusions stated |
| `repeat_testing` | Repeated and perturbed cases that examine Reliability's consistency, repeatability and robustness, not just one successful run |
| `sme_validation` | Named domain review of labels, consequences, coverage and unresolved disagreements |
| `control_evidence` | Observed implementation and effectiveness of required controls, including failure paths; if no extra controls are required, an observed review substantiating that conclusion |

There is no universal sample-size or pass-rate threshold in V1. Organizations must
set these before evaluation. The boolean adequacy field records that review; it
does not replace it. All factors must apply to the same assessment scope. The
model does not detect stale, fraudulent, unrelated, or statistically weak artifacts.

## Evidence maturity and confidence

[`evidence.py`](../src/ai_value_lab/evidence.py) applies these gates in order:

| Gate | Confidence | Evidence maturity |
| --- | --- | --- |
| All six factors have adequate Observed support | High | Corroborated observations |
| First three factors have adequate Observed support, but not all six | Medium | Covered observations |
| Core gate fails, with at least one Observed factor | Low | Limited observations |
| Core gate fails, with no Observed factors | Low | No observed evidence |

Every result includes the applicable rule, all six factor statuses/references,
and a gap for every unsupported factor. Removing any factor from High lowers
confidence; removing a core factor from Medium lowers it to Low. Removing another
factor while already Low cannot lower the label further but expands the gaps.
No averaging permits abundant evidence in one area to hide a missing core factor.
High confidence describes support for an assessment, not confidence that AI is safe.

## Controls and residual risk

[`controls.py`](../src/ai_value_lab/controls.py) contains four illustrative Payroll
control proposals, one for each top-level dimension. Each has a name, purpose,
dimension, evidence factor, effectiveness status, implementation flag and residual
rationale. Effectiveness is Unknown, Assumed, or Observed. Observed includes
measured support, but no numeric effectiveness is invented or inferred here.

Observed effectiveness requires an implemented control and adequate Observed
evidence. A reference must describe whether observations demonstrate effectiveness,
not merely the existence of a checklist. The `verified` property means these
supplied input conditions are met; it is not an independent verification service.

Residual behavior:

1. With no `ResidualReview`, retain inherent exposure as an **unverified planning
   carry-forward**. This is not a claim that actual residual risk was measured.
2. A review requires dimension, likelihood, impact, rationale, reviewer and adequate
   Observed evidence. The existing matrix derives exposure from the supplied pair.
3. Lowering either likelihood or impact requires at least one applicable implemented
   control with Observed effectiveness, even if the exposure band does not change.
4. Unchanged or worse ratings can be supported by observed evidence without control
   credit. Higher residual exposure must remain visible.

The reviewer must connect the specific failure modes, tested control bundle and
residual pair in the rationale. The model neither adds control effects nor reduces
an ordinal risk score by the economic control-effectiveness percentage. Multiple
controls can overlap or fail together; V1 does not model those dependencies.
All controls submitted to the decision function are treated as required for scope.

## Decision rules and precedence

[`decision.py`](../src/ai_value_lab/decision.py) accepts monthly economic value,
scoped evidence, exactly one risk per dimension, required controls, optional
residual reviews, ordinary unresolved gaps and critical gaps. Economic value is
an input from the existing formulas, not an independently verified financial fact.
Use value after assurance if the assessed controls are included in that scenario;
if their costs are missing, record an unresolved gap and do not assert adequate
observed economics. Zero/negative value is treated conservatively for this toolkit's
economic-value objective; a mandated/nonfinancial exception needs separate review.

First matching rule wins:

| Priority | Conditions | Posture |
| --- | --- | --- |
| 1 | Any critical gap, any evidence-supported High residual, or known monthly value at or below zero | Restricted deployment |
| 2 | Monthly value missing or confidence Low | Insufficient evidence |
| 3 | Confidence Medium or any remaining evidence/control/coverage/residual/unresolved gap | Pilot and gather evidence |
| 4 | Positive value, High confidence, no gaps, and required controls or Medium residual exposure | Proceed with controls |
| 5 | Positive value, High confidence, no gaps, no required additional controls, and supported Low residuals throughout | Proceed |

Every Medium/High inherent or residual dimension needs an applicable required
control before a Proceed posture. Required but proposed/unevidenced controls add
gaps. Every dimension needs a residual review to proceed. Synthetic High inherent
ratings carried forward without evidence are uncertainty, not evidence-supported
High residual findings: with no observations the default is Insufficient evidence.
Known critical blockers still outrank uncertainty. Critical gap severity is a human
input and must be explained; ordinary gaps cannot silently override a critical one.

Restricted deployment means broad use is blocked by a known constraint; it does
not authorize a narrower use automatically. Insufficient evidence means no supported
deployment conclusion. Pilot and gather evidence is an advisory proposal for a
separately approved, bounded evaluation with safeguards, not permission to expose
employees or sensitive data. Proceed postures are conditional recommendations
within the reviewed scope; the accountable human makes the actual decision.

Every output includes why, required controls, evidence gaps, residual risks,
confidence and what would change the recommendation. Reasons include all dimensions
and supplied control statuses, even when one earlier gate determines the posture.

## Human review and limits

Approve the rubric, coverage and evidence adequacy criteria, confidence gates,
critical-gap classification, residual judgments, control ownership, costs, and
risk acceptance before organizational use. The rules are intentionally conservative
design choices, not empirically validated deployment thresholds. Artifact freshness,
cross-scope consistency, quantitative uncertainty, and sign-off workflows remain
human responsibilities. See the [worked assessment](PAYROLL_ASSESSMENT.md).

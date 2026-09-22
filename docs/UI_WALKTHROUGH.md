# Three-step Streamlit walkthrough specification

**Implemented in `app.py`.** Three numbered sections remain visible on one page,
with sidebar jump links and links back to earlier sections. Standard Streamlit
components reuse the framework modules without changing formulas or risk ratings.
PreetiBuilds remains the canonical portfolio presentation layer.

## Shared behavior

Show the reasoning chain: Value → Reality → Risk → Evidence → Controls → Residual
Risk → Confidence → Decision. Keep the case category, scope and evidence provenance
visible across steps. Retain the existing economic defaults and four HR profiles.
Category selection changes risk context only, unless the user explicitly edits
economic inputs. Never relabel assumptions as observed when navigating steps.

In-page links support moving between stages without hiding results or losing inputs.
Derive outputs from the dedicated modules
on each change so a stale recommendation cannot survive revised evidence or costs.
Use expandable explanations for detail, readable tables and existing Streamlit
controls. Do not imply missing evidence is zero risk. No model calls or database.

Payroll Inquiry is the default. Evidence/control/review widget keys are scoped to
the selected category and scope text, so declarations do not silently transfer.
Changing category/scope starts new declarations; returning to an earlier category
does not promise persistent evidence. Economic inputs remain shared and unchanged.
References must be reviewed for relevance after changing economic assumptions.
Invalid declarations withhold the recommendation rather than keeping a stale result.

The existing four Payroll control proposals are editable declarations. Other
categories show missing category-specific controls rather than reusing Payroll
controls automatically. No arbitrary control-library editor is introduced.

## Step 1 — VALUE

**Purpose:** Determine whether the use case is economically worthwhile.

| Users see | Users provide | System derives |
| --- | --- | --- |
| Use-case summary, workflow boundary and Assumed/Synthetic badges | Scope and existing baseline/AI economic inputs | Baseline and AI cost, monthly/annual savings, simple payback using unchanged formulas |
| Existing economic comparison and calculation explanations | Adoption, effort, review, rework, service and implementation costs | A conditional economic comparison; non-positive savings and unavailable payback remain explicit |
| Provenance explanation | References to observations if available, with reviewer-defined adequacy | Clear separation of a calculated benefit from realized value |

Do not state that a positive result establishes safe deployment. Keep assurance
cost/effectiveness inputs accessible in Step 3 and reflect their effect back here
with a distinct before/after assurance result; preserve existing payback semantics.

## Step 2 — REALITY AND RISK

**Purpose:** Examine actual AI behavior and AI-related exposure.

| Users see | Users provide | System derives |
| --- | --- | --- |
| Four rows: Reliability, Privacy, Compliance, Operational Impact | HR category and scoped failure descriptions | Existing inherent profile and matrix exposure; default ratings remain synthetic |
| Reliability expansion: Accuracy, Consistency, Repeatability, Robustness | Relevant observations and references, or explicitly Missing/Assumed/Synthetic status | Evidence-supported factors and remaining gaps, never four extra top-level scores |
| Failure mode → dimension mapping, with Payroll illustrative example | Coverage, representativeness, repeat-testing and SME evidence declarations | Evidence maturity and Low/Medium/High confidence from `evidence.py` |
| “Not measured” for absent HR observations | Adequacy attestations against documented criteria | Per-factor reasons; no numeric confidence percentage |

Do not enable editing shipped inherent ratings until the review policy is approved.
Provide a rationale/help expansion explaining ordinal limits and domain calibration.
Changing evidence status to Observed requires a reference; marking non-observed
data adequate must show the validation error, not silently coerce it.

## Step 3 — ASSURANCE AND DECISION

**Purpose:** Show controls, evidence, residual risk, confidence and deployment posture.

| Users see | Users provide | System derives |
| --- | --- | --- |
| Four small Payroll control proposals or controls explicitly selected for scope | Control purpose/dimension, implementation status, evidence and effectiveness status | Validation and required-control evidence gaps |
| Inherent and residual exposure side by side with rationale | Optional observed residual review: likelihood, impact, reviewer, reference and rationale | `assess_residual` output; unverified carry-forward if no review |
| Existing assurance economics, clearly separate from risk reduction | Assumed or evidenced economic effectiveness and total relevant control cost | Existing prevented errors, avoided rework and net assurance value |
| Low/Medium/High confidence with maturity and reasons | Control evidence factor and unresolved/critical gaps | Updated confidence and ordered posture from `decision.py` |
| Why, required controls, evidence gaps, residual risks, what changes the decision | Human review of the complete scope and input declarations | Exactly one of the five V1 postures; no hidden aggregate score |

Show all five posture definitions in help. “Pilot” and “Restricted” are advisory,
not authorization. Keep observed/synthetic markers attached to supporting results.
Do not allow an assumed economic effectiveness percentage to downgrade ordinal
risk. Proposed controls remain unimplemented until supported declarations exist.

## Validation and manual browser checklist

`tests/test_app.py` uses Streamlit AppTest for headless behavior, not pixel tests.
Actual browser appearance, hover interactions and narrow widths still need review.

- Default Payroll reproduces the Markdown assessment: Low confidence,
  Insufficient evidence, four High unverified residual planning values.
- Navigation preserves inputs; changing evidence recomputes confidence and posture.
- Invalid evidence, residual and control inputs produce readable validation messages.
- Existing economics and four risk profiles remain identical for identical inputs.
- Small screens can read metrics and risk tables; sidebar controls remain reachable.
- Labels and expanders are keyboard accessible; color is never the sole status cue.
- UI tests cover the default journey, changed evidence, validation, category/scope
  switching, control/residual safeguards and rerun persistence. Verify jump links in a browser.
- Markdown download and Word/PDF export are later scope; no export promise in V1 UI.

Manual checks before portfolio capture:

- Step 1: change volume/adoption/rework; inspect savings, annual value and payback.
- Step 2: inspect all four profiles, rationales and Reliability's subordinate concepts.
- Step 3: inspect controls, assumed assurance economics, residual status and recommendation.
- Switch all case categories; economics stay constant and Payroll controls do not leak.
- Hover metric help and compare it with the displayed quantities.
- Confirm risk severity is distinct from confidence and evidence maturity.
- Inspect evidence gaps and explicit Missing/Synthetic/Assumed labels.
- Check invalid control evidence cannot produce a recommendation or risk reduction.
- Change evidence or economics and verify the recommendation recomputes.
- Narrow the browser; inspect metric stacking, table scrolling and readable captions.
- Open and close the sidebar; verify inputs and stage links remain accessible.
- Confirm no default screen implies observed HR evidence or measured effectiveness.

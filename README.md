# AI Value Lab

**AI Use Case Value and Assurance Assessment Toolkit**

Should we pursue this AI use case, under what conditions, and how confident are
we in that decision?

The current primary prototype is **AI-assisted employee HR case handling**:
General HR policy, Benefits, Employee data, and Payroll inquiry. AI retrieves,
summarizes and drafts guidance; it does not autonomously change payroll or employee
records, approve benefits, or make employment decisions.

**Status:** portfolio V1 framework prototype; package version remains `0.1.0`.
The three-step Streamlit journey presents economics, HR risk, evidence, controls,
residual review and deployment posture using reusable tested modules.
Payroll Inquiry is the default illustrative example. No validated HR
performance or measured HR control effectiveness is claimed.

**Terms:** source available, not open source. See [LICENSE](LICENSE), [NOTICE](NOTICE)
and [Terms of use](#terms-of-use).

## The assessment journey

1. **Value Assessment:** Is this AI use case economically worthwhile?
2. **Reality and Risk Assessment:** Does AI behave reliably enough in practice,
   and what AI-related exposure exists?
3. **Assurance and Decision:** What controls are required, what risk remains,
   how strong is the evidence, and what deployment posture is justified?

Value → Reality → Risk → Evidence → Controls → Residual Risk → Confidence → Decision

The project separates a promising business case from evidence of deployment
readiness. Positive savings alone cannot establish reliable behavior or acceptable
privacy, compliance, and operational exposure.

## Current capabilities and boundaries

| Component | Implemented now | Boundary |
| --- | --- | --- |
| Economics | Deterministic baseline, AI workflow, rework, review, service costs, savings and payback | Inputs are assumptions until measured; formulas unchanged |
| Assurance economics | Avoided rework cost minus control cost; remaining errors and rework cost | User-supplied effectiveness, not measured HR effectiveness; does not monetize all risk dimensions |
| Streamlit | Three numbered sections with jump links, economics, evidence declarations, control/residual review and explanations | Evidence is user-declared, not independently verified; Payroll control proposals do not transfer to other categories |
| Risk profiles | Four HR categories × Reliability, Privacy, Compliance, Operational Impact | Synthetic prototype likelihood/impact assumptions; exposure derived from them |
| Evidence and confidence | Six-factor deterministic Low/Medium/High confidence, reasons, maturity and gaps | Supplied evidence records are not independently verified; no confidence percentages |
| Controls and residual review | Four illustrative Payroll controls and evidence-gated residual assessment | Proposed controls earn no reduction credit; implementation is a declaration, not enforced by this software |
| Deployment posture | Five ordered, explainable advisory postures | Human approval and organization-specific calibration still required |
| Worked example | Payroll assessment in structured Markdown | Synthetic/assumed economics and illustrative controls; no HR evaluation results |
| Support research tools | Existing separate case set, policy pack, prompts, provider/runner, grader and analysis | Customer-support research slice, not evidence for the HR prototype |
| Validation | Unit tests and GitHub Actions Ruff/pytest configuration | Passing tests validate software contracts, not real-world HR outcomes |

The HR app and new assessment modules require no model API or API key. An existing
optional provider supports separate customer-support experiments; it is not called
by the app or these modules. This framework pass does not extend that provider.

## Evidence status and interpretation

- Default economic inputs and the Payroll example are **synthetic assumptions**.
  Derived dollar amounts are conditional model outputs, not realized savings.
- Current HR likelihood and impact ratings are **synthetic prototype assumptions**;
  inherent exposure is derived from those assumptions, not independently observed.
- The default 75% economic control effectiveness is **assumed**. It is not transferred
  into a risk-score reduction or used as confidence in deployment.
- The worked example's controls and failure modes are **illustrative** proposals.
  No deployed controls, actual incidents, observed HR evaluation coverage, or SME
  sign-off are asserted.
- Separate support dry runs or analysis tooling do not substantiate HR claims.
  [The support preregistration](docs/prereg-slice-01.md) describes that research
  slice; it must not be presented as completed HR validation.

Reliability remains one top-level dimension, supported by Accuracy, Consistency,
Repeatability, and Robustness. Risk severity and confidence are separate: strong
evidence may support a conclusion of High risk. See [Risk model](docs/RISK_MODEL.md)
and [Assessment rules](docs/ASSESSMENT_METHOD.md).

## Economics preserved

The engine lives in `src/ai_value_lab/value_model.py`, independently of Streamlit.
It compares current labor and rework costs with adopted/non-adopted work, human
review, AI service cost and AI rework. Time savings cannot reduce adopted direct
handling time below zero. Payback uses savings **before assurance** and is absent
when those savings are non-positive. Assurance value is avoided modeled rework
cost minus monthly control cost.

Default inputs include 10,000 monthly cases, 10 human minutes per case, $45/hour,
8% baseline rework, 70% AI adoption, six minutes saved per adopted case, 30% human
review and 6% AI rework. They are illustrative workload assumptions, not payroll
benchmarks. Selecting an HR category changes risk context, not economic inputs.
The review rate is a cost lever, not a defensible review policy without evidence.

The [Payroll assessment](docs/PAYROLL_ASSESSMENT.md) lists every economic input,
conditional result, evidence gap and the resulting Insufficient evidence posture.

## Reading and demonstration guide

- [Payroll Inquiry assessment source](docs/PAYROLL_ASSESSMENT.md): worked example
  and downloadable Markdown source for later Word/PDF conversion.
- [Risk model](docs/RISK_MODEL.md): dimensions, matrix, calibration and limitations.
- [Assessment method](docs/ASSESSMENT_METHOD.md): evidence, confidence, controls,
  residual review and ordered decision rules.
- [Three-step UI walkthrough](docs/UI_WALKTHROUGH.md): implemented journey,
  validation scope and remaining manual browser checks.
- [Portfolio positioning](docs/PORTFOLIO_POSITIONING.md): copy for later PreetiBuilds
  use. PreetiBuilds remains the independent canonical presentation layer.
- Existing `docs/decision-brief-support.html`, `docs/tradeoff-machine.html`,
  `docs/control-types.html`, support data and baseline notebook are separate
  illustrative/support materials, not the canonical Payroll assessment.
- `docs/DESIGN.md`, `docs/VALUE_FRAMEWORK.md`, `docs/ROADMAP.md` and
  `docs/agent_assurance_requirements.md` retain earlier design/planning context.
  This README and the V1 documents above describe current framework maturity.

## Repository structure

```text
app.py                         Existing Streamlit HR prototype
src/ai_value_lab/
    models.py, value_model.py   Existing economic/risk types and formulas
    risk_profiles.py           Existing four HR profiles
    evidence.py                Evidence maturity and confidence rules
    controls.py                Control records and residual reassessment
    decision.py                Advisory deployment posture rules
    scenarios.py               Economic scenario examples
    providers.py, runner.py     Separate support evaluation tooling
    grader.py, analysis.py      Support grading and statistical analysis
    prompts.py, validate_cases.py
cases/, policy_pack/            Synthetic customer-support evaluation inputs
data/, notebooks/              Earlier illustrative support materials
docs/                          Methodology, worked assessment and specifications
tests/                         Economics, risk, assessment and support-tool tests
.github/workflows/ci.yml        Ruff and pytest CI
```

## Setup and validation

Use Python 3.12 (the project pin); package metadata allows Python 3.12 through 3.14.
With `uv` already installed:

```bash
git clone https://github.com/pretzelslab/ai-value-lab
cd ai-value-lab
uv sync --extra dev
uv run streamlit run app.py
```

Recreate environments on each machine; do not copy `.venv`. See
[development setup](docs/dev-setup.md). Core dependencies and the lockfile remain
unchanged by the V1 framework pass.

```bash
uv run pytest
uv run ruff check .
```

CI runs pytest and Ruff. For a narrowly scoped change, also lint its modified Python
files without automatically fixing unrelated legacy files. Tests are deterministic
and do not require model calls. See the final validation report for the actual
runtime used in this workspace; a documented command is not proof of a clean run.

## Reusable V1 example

```python
from ai_value_lab import (
    AIInputs, AssuranceInputs, BaselineInputs,
    calculate_ai_scenario, calculate_assurance, get_risk_profile,
)
from ai_value_lab.controls import PAYROLL_CONTROLS
from ai_value_lab.decision import recommend_deployment
from ai_value_lab.evidence import EvidenceAssessment

ai = calculate_ai_scenario(BaselineInputs(), AIInputs())
assurance = calculate_assurance(ai, AssuranceInputs())
result = recommend_deployment(
    monthly_value=ai.monthly_savings + assurance.net_assurance_value,
    evidence=EvidenceAssessment("Payroll inquiry; illustrative monthly HR workflow"),
    risks=get_risk_profile("Payroll inquiry"),
    controls=PAYROLL_CONTROLS,
    unresolved_gaps=("Full C1-C4 control cost and review effort are unobserved.",),
)
assert result.posture == "Insufficient evidence"
assert result.confidence.level == "Low"
```

The evidence defaults deliberately remain Missing. Economic assumptions and a
control proposal do not become observations through calculation.

## Maturity and future scope

V1 is a coherent **framework prototype**, not a validated HR decision service.
The three-step Streamlit walkthrough now uses the tested modules while preserving
economics and default risk profiles. Next, manually review the browser workflow,
narrow-screen layout and methodological language before capturing portfolio assets.
Observed HR evaluations, reviewed control effectiveness, calibrated thresholds,
quantitative uncertainty, document export and portfolio promotion remain future
work. An integrated UI does not by itself establish real-world validity.

No model APIs, databases, authentication, RAG, agents or production monitoring are
introduced by this pass. The project is not an enterprise inventory, GRC replacement,
large control library or production observability platform.

## Data policy

Use synthetic data in the repository. Do not commit employee records, confidential
company information, credentials or PII. `evidence/` and `docs/internal/` are ignored;
that is not permission to publish their contents. Reference authorized evidence
without copying sensitive records into the toolkit. Optional experiment credentials
belong in environment configuration, never source code.

## Terms of use

**This repository is source available, not open source.** It is publicly readable. It is not licensed under any OSI approved licence and no such licence should be inferred from its visibility.

In short:

- You may read, study, run locally, and reference this work.
- You may not use it, or derivative works, for commercial purposes without written permission.
- You may not use the methodology, metrics, rubrics or evaluation design as the basis of a competing product or framework.
- You may not present this work or its outputs as your own.
- Attribution is required for any reference.

Commercial use may be granted on request. See [LICENSE](LICENSE) for the full terms and [NOTICE](NOTICE) for what is deliberately held back from this repository and why.

The methodology, rubrics, failure mode taxonomy, evaluation design and case sets are the substantive contribution. The application code is the smaller part.

## Citing this work

If this methodology or its metrics inform your work, cite it. Machine readable metadata is in [CITATION.cff](CITATION.cff).

> Raghuveeran, P. (2026). *AI Value Lab: evidence driven AI use case assessment.* https://github.com/pretzelslab/ai-value-lab

## Contributing

This is a single author research project and is not accepting pull requests at this stage.

Issues raising methodological problems, arithmetic errors, or gaps in the reasoning are welcome and valued. A correction to the model is worth more than a feature.

## Disclaimer

This toolkit produces assessments and recommendations about AI deployment. It does not constitute legal, regulatory, financial or professional advice. Outputs depend entirely on the inputs and assumptions supplied by the user, and the majority of those inputs are currently unmeasured assumptions. Responsibility for any deployment decision rests with the organisation making it.

## Project status

Package version: `0.1.0`. Portfolio V1 framework prototype with the three-step
assessment chain integrated into Streamlit. No production
readiness or validated HR deployment recommendation is claimed.

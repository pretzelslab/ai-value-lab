# AI Value Lab

AI Value Lab is a hands on project for testing when an enterprise AI use case creates measurable economic value compared with the current way of working.

The first use case is intentionally simple: a customer support workflow. The project starts with transparent business assumptions and deterministic calculations. Later phases replace assumptions with evidence from real language model experiments.

**Status:** research prototype, version 0.1.0. Economics engine working and tested. Evidence layer not yet built. See [Maturity](#maturity) for an honest account.

**Terms:** source available, not open source. See [LICENSE](LICENSE) and [Terms of use](#terms-of-use) before using any part of this.

## Why this project exists

AI business cases often jump directly to model cost or headline productivity claims. This project starts with a different sequence:

```text
Current workflow
      |
      v
Economic baseline
      |
      v
AI intervention
      |
      v
AI enabled economics
      |
      v
Scenario and sensitivity testing
      |
      v
Observed model performance
      |
      v
Realized AI value
```

The goal is not to produce a single ROI number. The goal is to understand which operational, technical, and adoption conditions make an AI investment economically worthwhile.

### The narrow claim

Most AI business cases rest on an assumed control effectiveness figure that nobody measured. That figure is not academic. It determines the defensible human review rate, and the review rate is the single largest lever on the size of the saving.

This project's distinctive claim is that it **prices the control**: it converts evaluation evidence into a measured control effectiveness, carries the resulting residual risk into the business case, and shows what each point of risk removed actually costs.

## Current scope

Version 0.1 includes:

1. A deterministic current state cost model
2. A deterministic AI enabled cost model
3. Human review, AI rework, AI service cost, adoption, and implementation cost
4. Monthly value, annual value, cost per case, and payback calculations
5. A minimal Streamlit interface for changing assumptions
6. Unit tests for the economics engine
7. A baseline Jupyter notebook
8. Synthetic sample data
9. Design, methodology, and roadmap documentation
10. GitHub Actions continuous integration

No language model API is required in this phase.

## What is deliberately not included yet

1. Model API calls
2. Token level pricing
3. Prompt evaluation
4. Monte Carlo simulation
5. Persistent database storage
6. Authentication
7. Multi use case portfolio management
8. AI safety and governance controls

These are later milestones so that the economics remains understandable before complexity is introduced.

## What is deliberately out of scope entirely

Not later milestones. Not being built.

1. An enterprise AI inventory or model registry
2. A replacement for a GRC platform
3. A generic regulatory questionnaire or a large control library
4. A production model observability platform
5. An LLM gateway, RAG system or agent framework

## Principles

These are intended to be enforced by the code rather than by discipline. Where the code does not yet enforce one, that is recorded as a defect rather than quietly tolerated.

1. **No important number without a rationale.**
2. **No confidence without evidence.** `NotAssessed` is a legal return value. The model must not emit a confidence figure it has no basis for.
3. **No control effectiveness without measurement**, once evaluation evidence exists.
4. **No recommendation without traceability.** Every displayed number expands into its inputs, its formula, and its provenance.
5. **Every value carries a provenance tag:** `assumed`, `user_supplied`, `measured`, or `derived`.
6. **Two significant figures, always with an interval.** A point estimate implies a precision that sixty test cases cannot support.

## Architecture

```text
                    AI VALUE LAB

                  Streamlit UI
                       |
                       v
                Scenario inputs
                       |
                       v
             +-------------------+
             |   Value Model     |
             +-------------------+
                |             |
                v             v
        Current baseline   AI scenario
                |             |
                +------|------+
                       v
                Economic results
                       |
          +------------+-------------+
          |            |             |
          v            v             v
      Notebooks       Tests       Future APIs
```

The central design rule is that the economics engine lives in `src/ai_value_lab/` and does not depend on Streamlit. This makes the calculations reusable from notebooks, tests, APIs, future model experiments, or another frontend.

See `docs/DESIGN.md` for the fuller design.

## Repository structure

```text
ai-value-lab/

README.md
LICENSE
NOTICE
CITATION.cff
pyproject.toml
uv.lock
.python-version
.gitattributes
app.py

src/ai_value_lab/
    models.py
    value_model.py
    scenarios.py
    risk_profiles.py

data/
    sample_support_cases.csv

notebooks/
    01_baseline.ipynb

docs/
    DESIGN.md
    VALUE_FRAMEWORK.md
    ROADMAP.md
    dev-setup.md
    prereg-slice-01.md

tests/
    test_value_model.py

.github/workflows/
    ci.yml
```

## Technology choices

### Python 3.12

Python 3.12 is pinned as the default project version to keep local development and future Streamlit deployment consistent.

### uv

`uv` manages the virtual environment and dependency lockfile. `uv.lock` is committed, so dependency resolution is identical on every machine.

### Streamlit

Streamlit provides the first interactive interface. It is intentionally treated as a presentation layer rather than the place where economic calculations live.

### pytest

Tests verify the economic calculations independently of the user interface.

### Ruff

Ruff provides lightweight linting so the repository stays clean as it grows.

## Setup on a new computer

Install `uv` once on the computer.

macOS or Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then clone the repository and recreate the environment:

```bash
git clone https://github.com/pretzelslab/ai-value-lab
cd ai-value-lab
uv sync --extra dev
```

Run the tests:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

Start the application:

```bash
uv run streamlit run app.py
```

Start Jupyter Lab:

```bash
uv run jupyter lab
```

Open `notebooks/01_baseline.ipynb`.

This project has moved between macOS and Windows. See [docs/dev-setup.md](docs/dev-setup.md) for the cross platform rules that keep both machines producing identical results. The short version: never copy a virtual environment or a working folder between machines, always clone.

## First hands on exercise

Do not change the AI assumptions first.

Start with the current workflow.

The default baseline assumes:

| Input | Default |
| --- | ---: |
| Monthly support cases | 10,000 |
| Human minutes per case | 10 |
| Loaded hourly cost | $45 |
| Rework rate | 8% |
| Minutes per rework | 6 |

The baseline model calculates direct labor cost, rework cost, total monthly operating cost, and cost per case.

Run:

```bash
uv run pytest
uv run streamlit run app.py
```

Then change one assumption at a time and explain why the result changes.

The objective of Milestone 1 is not to optimize the AI scenario. It is to understand the current state economics well enough that every baseline number is defensible.

## AI value model

The first AI scenario introduces:

| Driver | Meaning |
| --- | --- |
| Adoption rate | Share of cases where the AI capability is actually used |
| Minutes saved | Human effort removed from an AI assisted case |
| Human review rate | Share of AI assisted cases receiving review |
| Review minutes | Human effort consumed by each review |
| AI cost per case | Estimated model or service cost for each assisted case |
| AI rework rate | Share of AI assisted cases requiring corrective work |
| AI rework minutes | Human effort needed for correction |
| Implementation cost | One time cost used for simple payback |

These are intentionally separate. High technical performance does not automatically create realized business value if adoption is low or human review remains expensive.

Of these, **human review rate is the dominant lever.** Holding everything else constant, moving review from every AI answer to one in ten roughly doubles the annual saving. Nothing about the model's capability sets that rate. Only evidence about its failure rate does, which is why the evaluation work below is part of the value model rather than a separate risk exercise.

## Value outputs

Version 0.1 produces:

1. Current monthly operating cost
2. AI enabled monthly operating cost
3. Current cost per case
4. AI enabled cost per case
5. Monthly economic value
6. Annual economic value
7. Simple payback period
8. Remaining human hours
9. AI service cost

Later versions will add break even thresholds, sensitivity analysis, uncertainty distributions, quality adjusted value, and realized value.

## Evidence status

The assessments this repository produces are only as good as the evidence behind them. Stated plainly:

- **Every economic input is `assumed`.** None has been measured.
- **Control effectiveness is `assumed`.** No evaluation has been run.
- **Risk ratings are authored judgements** with written rationales. They are not measurements.

The first measured slice is preregistered before any data is collected. See [docs/prereg-slice-01.md](docs/prereg-slice-01.md). Its protocol, case set, grader and analysis plan are committed before the first model call, so the analysis cannot be selected after seeing the results. Departures from the protocol are appended to `docs/deviations.md` with a date and a reason.

Evidence records carry the model identifier, model version and date, and expire when the model version changes. A measurement taken against one model version does not transfer to another.

## Maturity

Published honestly, because an overstated maturity claim is the fastest way to lose a technical reader.

| Component | State |
| --- | --- |
| Baseline and AI workflow economics | Built |
| Assurance economics, assumed control effectiveness | Built |
| Payback, transparent calculation explanations | Built |
| Case based risk profiles, 4 contexts x 4 dimensions | Built, prose form |
| Canonical assessment model | Not written |
| Failure mode records | Not built |
| Evidence records and provenance types | Not built |
| Measured control effectiveness | Not built |
| Confidence derivation | Not built |
| Decision layer with hard vetoes | Not built |

Demo completeness is roughly 80 percent. The full evidence driven toolkit is roughly 20 to 25 percent, because the five unbuilt rows are the toolkit.

## Portfolio development path

The project is designed so each milestone leaves behind something demonstrable.

```text
Milestone 0
Portable repository and tested foundation

Milestone 1
Current state economic baseline

Milestone 2
AI enabled economics

Milestone 3
Scenario and break even analysis

Milestone 4
Sensitivity analysis

Milestone 5
Monte Carlo uncertainty simulation

Milestone 6
Real LLM workload experiments

Milestone 7
Observed cost, latency, and quality

Milestone 8
Potential value versus realized value

Milestone 9
Multi use case AI value portfolio
```

See `docs/ROADMAP.md` for the working roadmap.

## Claude and other coding assistants

Claude is not required to install, run, understand, or extend this project.

The repository uses standard Python, Jupyter, Streamlit, pytest, and Git. A fresh computer only needs Git plus either `uv` or a compatible Python installation.

Claude Code, Codex, or another coding assistant can be added later as a development accelerator for tasks such as generating repetitive UI code, refactoring, writing additional tests, or implementing a well defined feature. The application itself should never depend on a coding assistant.

This distinction is intentional:

```text
Required to run the product        Optional to help build the product

Python                             Claude Code
Dependencies                       Codex
Git                                Other coding assistants
Application source
```

## Reproducibility rule

Whenever dependencies change, commit both `pyproject.toml` and the updated `uv.lock`.

Before pushing a change, run:

```bash
uv run ruff check .
uv run pytest
```

GitHub Actions repeats linting and tests after a push or pull request.

The economic model must be deterministic: the same inputs produce the same outputs, byte for byte, on any machine. No wall clock, no locale dependent formatting, and no unordered iteration inside the calculation modules.

## Data policy

The starter repository uses synthetic data only.

Do not place customer records, confidential company information, API keys, or personally identifiable information in the repository.

Future API keys should be stored locally in `.env` or in the deployment platform's secrets manager. `.env` is already excluded from Git.

The evaluation policy pack describes a fictitious company and is written so that ground truth is knowable without publishing any real organisation's commitments. Every evidence record states whether its underlying data is synthetic.

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

Current version: `0.1.0`

Current milestone: portable foundation and baseline economics.

Next milestone: the first preregistered measurement, replacing assumed control effectiveness with a measured figure. See [docs/prereg-slice-01.md](docs/prereg-slice-01.md).

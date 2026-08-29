# AI Value Lab

AI Value Lab is a hands on project for testing when an enterprise AI use case creates measurable economic value compared with the current way of working.

The first use case is intentionally simple: a customer support workflow. The project starts with transparent business assumptions and deterministic calculations. Later phases can replace assumptions with evidence from real language model experiments.

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
ai_value_lab/

README.md
pyproject.toml
.python-version
app.py

src/ai_value_lab/
    models.py
    value_model.py
    scenarios.py

data/
    sample_support_cases.csv

notebooks/
    01_baseline.ipynb

docs/
    DESIGN.md
    VALUE_FRAMEWORK.md
    ROADMAP.md

tests/
    test_value_model.py

.github/workflows/
    ci.yml
```

## Technology choices

### Python 3.12

Python 3.12 is pinned as the default project version to keep local development and future Streamlit deployment consistent.

### uv

`uv` manages the virtual environment and dependency lockfile. The first `uv sync` creates `uv.lock`. Commit that generated lockfile to Git so future setup is reproducible across computers.

### Streamlit

Streamlit provides the first interactive interface. It is intentionally treated as a presentation layer rather than the place where economic calculations live.

### pytest

Tests verify the economic calculations independently of the user interface.

### Ruff

Ruff provides lightweight linting so the repository stays clean as it grows.

## Setup on a new computer

### Recommended setup with uv

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
git clone YOUR_GITHUB_REPOSITORY_URL
cd ai_value_lab
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

## Setup without uv

A conventional Python environment also works.

```bash
python -m venv .venv
```

Activate the environment using the command appropriate for the operating system, then run:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
streamlit run app.py
```

`uv` is recommended because the lockfile gives stronger reproducibility across machines.

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
Dependencies                      Codex
Git                               Other coding assistants
Application source
```

## Reproducibility rule

On the first successful `uv sync`, commit the generated `uv.lock` file. After that, whenever dependencies change, commit both `pyproject.toml` and the updated `uv.lock` file.

Before pushing a change, run:

```bash
uv run ruff check .
uv run pytest
```

GitHub Actions repeats linting and tests after a push or pull request.

## Data policy

The starter repository uses synthetic data only.

Do not place customer records, confidential company information, API keys, or personally identifiable information in the repository.

Future API keys should be stored locally in `.env` or in the deployment platform's secrets manager. `.env` is already excluded from Git.

## Project status

Current version: `0.1.0`

Current milestone: portable foundation and baseline economics.

Next milestone: validate the baseline assumptions and add scenario comparison without changing the architecture.

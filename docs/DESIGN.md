# Design

## Design goal

AI Value Lab is designed as a small, inspectable decision model first and a richer application later.
The economics engine must remain understandable enough that every output can be traced back to a business assumption.

## Design principles

1. Economics before interface
2. Explicit assumptions before conclusions
3. Baseline before AI comparison
4. Reusable calculation logic outside the UI
5. Synthetic data before confidential enterprise data
6. Tests for calculations before adding complexity
7. One use case first, multiple use cases later
8. Real model telemetry can replace assumptions later without changing the core framework

## Logical architecture

```text
User
  |
  v
Streamlit UI
  |
  v
Scenario Inputs
  |
  v
Value Model
  |          |
  |          +--> Current State Model
  |
  +-------------> AI Enabled Model
  |
  v
Economic Results
  |
  +--> Cost per case
  +--> Monthly value
  +--> Annual value
  +--> Payback
  +--> Human hours
  +--> AI service cost
```

## Package boundaries

`src/ai_value_lab/models.py`
Defines inputs and outputs. It should contain no UI code.

`src/ai_value_lab/value_model.py`
Contains deterministic economic calculations and validation.

`src/ai_value_lab/scenarios.py`
Contains named example scenarios. Future scenarios should be data driven.

`app.py`
Contains only presentation and user input wiring.

`tests/`
Validates economics independently of Streamlit.

`notebooks/`
Used for exploration, sensitivity analysis, and research notes. Calculations that become stable should move into `src/`.

## Extension path

Phase 1: deterministic value model

Phase 2: scenario comparison and break even analysis

Phase 3: sensitivity analysis and Monte Carlo simulation

Phase 4: real LLM experiment runner

Phase 5: token, latency, quality, and cost telemetry

Phase 6: use case portfolio and enterprise value dashboard

## Future integration boundary

The current field `ai_cost_per_adopted_case` is deliberately simple.
Later it can be derived from actual model traces:

```text
Prompt tokens
+ Completion tokens
+ Model price
+ Retry cost
+ Tool cost
+ Review cost
= Observed cost per successful task
```

The rest of the economic model should not need to be rewritten when this happens.

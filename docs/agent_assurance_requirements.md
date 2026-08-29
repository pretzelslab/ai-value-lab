# Agent Assurance Value Lab Requirements

## 1. Purpose

The Agent Assurance Value Lab extends the existing AI Value Lab to measure not only the economic benefit of AI assisted work, but also the value impact of AI agent failures and assurance controls.

The lab should help answer:

> Does adding assurance increase the expected business value of deploying an AI agent?

The model should make every displayed value traceable to a clearly defined input, assumption, or formula.

## 2. Problem Statement

Traditional AI ROI models often estimate value using labor savings, productivity improvement, or service cost reduction.

Agentic systems introduce additional economic factors:

- AI outputs may fail.
- Failures may require human remediation.
- Some failures may create direct incident costs.
- Assurance controls may reduce failure exposure.
- Assurance controls also introduce cost and potentially additional operational overhead.

The lab should quantify these tradeoffs so users can compare gross AI value, failure adjusted value, and assurance adjusted value.

## 3. Current Baseline

The existing AI Value Lab calculates the economic impact of introducing AI assistance into a workflow.

Current baseline inputs and outputs include:

### Inputs

- Total cases
- AI assisted percentage
- Human handling time per case
- Human hourly cost
- AI cost per assisted case

### Derived Values

- AI assisted cases
- Remaining human handled cases
- Remaining human hours
- Human cost
- AI service cost
- Total operating cost
- Estimated AI value or savings

The existing model becomes the baseline for all assurance calculations.

## 4. Target Users

Initial target users include:

- AI Product Managers
- Program and Transformation Leaders
- AI Governance and Risk Teams
- Engineering Leaders
- Operations Leaders
- Enterprise AI Decision Makers

## 5. Core Use Cases

### UC1. Estimate AI Value

A user enters workload and cost assumptions and receives the economic value of introducing AI assistance.

### UC2. Estimate Failure Exposure

A user enters an expected AI failure rate and remediation assumptions and receives the expected cost of failures.

### UC3. Estimate Failure Adjusted AI Value

The lab calculates how expected failures reduce the apparent value of AI adoption.

### UC4. Apply an Assurance Control

A user enables an assurance control and specifies its expected effectiveness and operating cost.

### UC5. Calculate Assurance Value

The lab calculates the value created by reducing expected failure costs, net of the cost of the assurance control.

### UC6. Compare Scenarios

The user compares AI without failure adjustment, AI with expected failures, and AI with assurance.

## 6. Functional Requirements

### FR1. Preserve Existing Baseline

The existing AI economics calculations must continue to work without modification to their meaning.

### FR2. Accept Failure Inputs

The system must accept:

- Failure rate
- Average remediation time per failure
- Human hourly cost
- Average incident cost per failure

### FR3. Calculate Expected Failures

Formula:

Expected Failures = AI Assisted Cases × Failure Rate

### FR4. Calculate Remediation Hours

Formula:

Remediation Hours = Expected Failures × Remediation Time Per Failure

### FR5. Calculate Remediation Labor Cost

Formula:

Remediation Labor Cost = Remediation Hours × Human Hourly Cost

### FR6. Calculate Incident Cost

Formula:

Expected Incident Cost = Expected Failures × Average Incident Cost Per Failure

### FR7. Calculate Expected Failure Cost

Formula:

Expected Failure Cost = Remediation Labor Cost + Expected Incident Cost

### FR8. Calculate Failure Adjusted AI Value

Formula:

Failure Adjusted AI Value = Baseline AI Value − Expected Failure Cost

### FR9. Support One Assurance Control in V1

The system must support one generic assurance control with these inputs:

- Control enabled
- Control effectiveness percentage
- Control operating cost

### FR10. Calculate Residual Failure Rate

Formula:

Residual Failure Rate = Failure Rate × (1 − Control Effectiveness)

### FR11. Calculate Residual Expected Failures

Formula:

Residual Expected Failures = AI Assisted Cases × Residual Failure Rate

### FR12. Calculate Residual Failure Cost

Residual failure cost must use the same remediation and incident cost assumptions as the unprotected failure model.

### FR13. Calculate Avoided Failure Cost

Formula:

Avoided Failure Cost = Expected Failure Cost − Residual Failure Cost

### FR14. Calculate Assurance Value

Formula:

Assurance Value = Avoided Failure Cost − Assurance Control Cost

### FR15. Calculate Protected Net AI Value

Formula:

Protected Net AI Value = Baseline AI Value − Residual Failure Cost − Assurance Control Cost

### FR16. Scenario Comparison

The system must display at least three scenarios:

1. AI baseline, failures not considered
2. AI with expected failures
3. AI with assurance control

## 6.1 V1 Reference Use Case: Customer Support

### Team

Customer Support

### Need

Reduce handling effort for repetitive or well documented support cases while maintaining human review of AI generated resolutions.

### Reference Scenario

| Input | Value |
|---|---:|
| Support cases per month | 10,000 |
| Average handling time without AI | 20 minutes |
| AI assisted cases | 70% |
| Handling time for AI assisted case | 8 minutes |
| Human hourly cost | $45 |
| AI service cost per assisted case | $0.10 |
| AI failure rate | 4% |
| Additional remediation time per failure | 15 minutes |

These values are illustrative assumptions for validating the V1 model and are not intended to represent industry benchmarks.

### Value Questions

1. What does the support workflow cost without AI?
2. What value does AI assistance create?
3. How much value is lost because of AI failures?
4. How much of that loss can an assurance control prevent?
5. Does the value of avoided failures justify the cost of assurance?

### Initial Failure Definition

For this use case, a failure means an AI assisted support case that requires additional corrective human work because the proposed resolution was incorrect or unusable.

Remediation time represents only additional work caused by the AI failure. It does not include normal human review time already included in the baseline workflow.

### V1 Principle

This scenario is a reference case for validating the economics of the model.

It is not intended to represent an industry benchmark.

## 7. Failure Model

V1 uses a single aggregate failure rate.

Examples of failures represented by this aggregate may include:

- Incorrect output
- Failed task completion
- Human escalation caused by AI error
- Tool misuse
- Policy violation

V1 will not model each failure category independently.

### Failure Inputs

| Input | Description | Example |
|---|---|---:|
| Failure Rate | Percentage of AI assisted cases expected to fail | 3% |
| Remediation Time | Human effort required to resolve one failure | 20 minutes |
| Human Hourly Cost | Labor cost used for remediation | $45 |
| Incident Cost | Additional average non labor cost per failure | $25 |

## 8. Assurance Control Model

V1 will use one generic assurance control.

The control represents any mechanism designed to reduce agent failure probability.

Examples may include:

- Policy enforcement
- Tool call validation
- Human approval
- Output validation
- Monitoring

These controls are examples only. V1 does not model them separately.

### Assurance Inputs

| Input | Description | Example |
|---|---|---:|
| Control Enabled | Whether assurance is applied | Yes |
| Control Effectiveness | Percentage reduction in failure probability | 75% |
| Control Cost | Cost of operating the assurance control | $8,000 |

## 9. Calculation Logic

The calculation sequence is:

```text
Total Workload
      |
      v
AI Assisted Cases
      |
      v
Baseline AI Value
      |
      v
Expected Failure Rate
      |
      v
Expected Failures
      |
      +--> Remediation Cost
      |
      +--> Incident Cost
      |
      v
Expected Failure Cost
      |
      v
Failure Adjusted AI Value
      |
      v
Assurance Control
      |
      v
Residual Failure Rate
      |
      v
Residual Failure Cost
      |
      v
Avoided Failure Cost
      |
      v
Assurance Value
      |
      v
Protected Net AI Value
```

## 10. Required Inputs

### Existing Inputs

- Total cases
- AI assisted percentage
- Human handling time
- Human hourly cost
- AI cost per assisted case

### New V1 Inputs

- Failure rate
- Remediation time per failure
- Average incident cost per failure
- Assurance control enabled
- Assurance control effectiveness
- Assurance control cost

## 11. Expected Outputs

The lab should display:

### Baseline Economics

- AI assisted cases
- Remaining human hours
- Human cost
- AI service cost
- Baseline AI value

### Failure Exposure

- Expected failures
- Remediation hours
- Remediation labor cost
- Expected incident cost
- Expected failure cost
- Failure adjusted AI value

### Assurance

- Residual failure rate
- Residual expected failures
- Residual failure cost
- Avoided failure cost
- Assurance control cost
- Assurance value
- Protected net AI value

## 12. Scenario Comparison

The following scenarios must be supported:

| Scenario | Description |
|---|---|
| Scenario A | AI economics without considering failures |
| Scenario B | AI economics including expected failure costs |
| Scenario C | AI economics including assurance controls |

The comparison should make the economic impact of failure exposure and assurance visible.

## 13. UI Requirements

V1 UI changes should remain simple.

The Streamlit application should eventually include:

- Existing baseline economics section
- Failure assumptions section
- Failure exposure results
- Assurance control section
- Assurance value results
- Scenario comparison

UI implementation should begin only after calculation logic and unit tests are complete.

## 14. Assumptions

V1 assumes:

- Failure rate is applied uniformly across AI assisted cases.
- Failures are independent for calculation purposes.
- Remediation effort is represented by an average value.
- Incident cost is represented by an average value.
- Control effectiveness reduces the failure probability proportionally.
- Assurance operating cost is entered directly by the user.
- The model estimates expected economic exposure, not guaranteed realized losses.
- All values are scenario assumptions rather than industry benchmarks.

## 15. Out of Scope for V1

The following are intentionally excluded:

- NIST AI RMF mapping
- EU AI Act mapping
- OWASP taxonomy
- Detailed attack taxonomy
- Multiple independent failure types
- Multiple assurance controls
- Monte Carlo simulation
- Multi agent systems
- Real model evaluations
- Real time monitoring
- Production telemetry
- Automated control recommendations
- Industry benchmarking
- Detailed severity tiers
- Probabilistic dependencies between failures
- Latency impact modelling
- Compliance penalty modelling

## 16. Acceptance Criteria

V1 is complete when the system can:

- Accept a failure rate.
- Calculate expected failures.
- Calculate remediation hours.
- Calculate remediation labor cost.
- Calculate expected incident cost.
- Calculate total expected failure cost.
- Calculate failure adjusted AI value.
- Enable or disable one assurance control.
- Calculate residual failure rate.
- Calculate residual expected failures.
- Calculate residual failure cost.
- Calculate avoided failure cost.
- Calculate assurance value.
- Calculate protected net AI value.
- Compare the three defined scenarios.
- Trace every displayed value to an input or formula.
- Pass unit tests for all new calculation functions.

## 17. Non Functional Requirements

### NFR1. Traceability

Every displayed metric must be explainable using visible inputs and documented formulas.

### NFR2. Simplicity

V1 should prioritize understandable economics over sophisticated risk modelling.

### NFR3. Testability

Calculation logic must be separated from Streamlit UI logic and covered by unit tests.

### NFR4. Extensibility

The data model should allow future addition of multiple failure categories and multiple assurance controls without requiring a complete redesign.

### NFR5. Transparency

The application must clearly distinguish user supplied assumptions from calculated results.

## 18. Future Enhancements

Potential future extensions include:

- Multiple failure categories
- Severity based incident modelling
- Multiple assurance controls
- Control stacking
- Diminishing returns across controls
- Low, medium, and high risk workflow profiles
- Agent autonomy levels
- Human in the loop economics
- Tool permission modelling
- Policy enforcement economics
- Observability and monitoring costs
- Monte Carlo simulation
- Sensitivity analysis
- Industry benchmarks
- NIST AI RMF mapping
- EU AI Act mapping
- Governance maturity scoring
- Recommended assurance packages
- Production telemetry ingestion

## 19. V1 Value Proposition

The Agent Assurance Value Lab should demonstrate one simple idea:

```text
AI creates economic value
        |
        v
Agent failures erode some of that value
        |
        v
Assurance controls reduce expected failures
        |
        v
Controls themselves have a cost
        |
        v
Avoided Losses − Control Cost
        |
        v
ASSURANCE VALUE
```

The goal is not to prove that more controls are always better.

The goal is to determine when assurance economically improves the deployment of an AI agent.

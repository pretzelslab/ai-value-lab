# AI Use Case Value and Assurance Assessment Toolkit

**Content prepared for later PreetiBuilds use; no portfolio integration or publication
has occurred.** Recommended presentation status: Preview / framework prototype.

## One-sentence description

AI Value Lab connects the economics of an AI-assisted HR workflow to reliability,
risk, evidence, controls and an explainable deployment posture.

## Core question

Should we pursue this AI use case, under what conditions, and how confident are
we in that decision?

## Short overview

This Python toolkit starts with a transparent business case, then asks what
evidence supports AI performance and the controls needed for use. A Payroll Inquiry
example connects Value → Reality → Risk → Evidence → Controls → Residual Risk →
Confidence → Decision while making synthetic assumptions and evidence gaps explicit.

## Problem

An attractive savings estimate can hide uncertainty about AI behavior, sensitive
data handling and the effort needed to control failures. Decision makers need to
distinguish potential economic value from supported deployment readiness.

## Approach

Keep economic calculations deterministic and independently tested. Assess four
dimensions—Reliability, Privacy, Compliance and Operational Impact—and support
Reliability with Accuracy, Consistency, Repeatability and Robustness. Apply
transparent evidence gates, require support before crediting risk reduction, and
return a posture with reasons rather than a single combined score.

## What was built

- A Streamlit HR prototype with baseline/AI/assurance economics and four HR profiles.
- Reusable qualitative evidence-maturity and confidence classification.
- Four illustrative Payroll controls and evidence-gated residual reassessment.
- Five deterministic advisory deployment postures with explanations and gaps.
- A Payroll worked assessment in structured Markdown, tests, and a future
  three-step UI specification.

The new assessment modules run independently of Streamlit; their UI integration
is pending. Existing separate customer-support evaluation tooling is research
infrastructure, not validated HR evidence.

## Current limitations

HR economic inputs, profile ratings and control effectiveness remain assumptions.
No observed HR evaluations, production controls, measured HR savings or deployment
approval are claimed. The evidence adequacy and decision rubric need domain-owner
calibration. The toolkit validates declarations and rule consistency, not the
truth or freshness of external evidence. No live demo URL is asserted here.

## What makes the framework useful

The framework makes decision dependencies inspectable. A reviewer can see why
positive assumed economics still produce Insufficient evidence, identify which
controls need evaluation, and understand what would change the posture. Keeping
risk and confidence separate avoids treating uncertainty as reassurance.

## Prototype status language

“Portfolio V1 framework prototype. Deterministic economics and advisory assessment
rules, illustrated with synthetic HR assumptions. New framework logic is tested
separately from the current Streamlit interface. Not a validated HR decision
service or production deployment.”

## Suggested portfolio metadata and assets

- Category: Enterprise Assessment & Decision Systems.
- Title: AI Value Lab.
- Tags: Python, Streamlit, pytest, AI Assurance, Decision Support.
- Industries: Enterprise HR, Payroll Operations.
- Status: Preview; locking is a separate presentation decision.
- GitHub: repository origin is `https://github.com/pretzelslab/ai-value-lab`;
  verify public access before adding the portfolio CTA.
- Proposed internal route: `/ai-value-lab`, not created in this pass.
- Screenshots/demo: capture and review in a later pass; do not present synthetic
  examples as live activity. PreetiBuilds owns the presentation and asset layout.
- Licensing: source available, not open source; retain LICENSE/NOTICE attribution.

No claims of market uniqueness, validated outcomes or measured effectiveness are
needed to explain the project's value.

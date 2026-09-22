# UI clarity and portfolio alignment

## Read-only reference

PreetiBuilds `src/index.css`, `src/pages/AIPlatform.tsx`, and `src/pages/MedLog.tsx`
were inspected without changes. The pages vary, but share bounded content,
generous section spacing, muted explanatory text, rounded cards, subtle borders,
small status labels and responsive layouts.

- Body font: Space Grotesk; monospace labels: JetBrains Mono. Syne is also imported
  globally, but the inspected page headings do not explicitly require it.
- Content: AI Platform uses `max-w-5xl`, MedLog `max-w-3xl`, both with `px-6` margins.
- Headings: roughly 30px main titles, 20px section headings, 14px explanatory prose;
  larger introductory text and smaller captions establish hierarchy.
- Palette: cool off-white / dark navy backgrounds, neutral card fills and borders,
  purple/teal theme accents; blue, amber and emerald are used for context/status.
- Corners: 0.75rem theme radius; compact badges often use pill shapes.
- Spacing: common 1–1.5rem card padding and 2.5–3rem section spacing.
- Links: muted text with foreground/accent hover; clear back navigation.
- Responsive layouts: bounded fluid widths, wrapping tags, single-column layouts
  expanding at breakpoints; no universal fixed screenshot or page width.

## Streamlit translation

`.streamlit/config.toml` uses the reference light palette with native Streamlit
widgets. `assets/portfolio.css` caps content at 64rem while allowing it to shrink,
uses wrapping summary cards and compact metric rows, and keeps native hover help.
On narrow screens, metric values stack below their labels. No fixed desktop width,
remote font fetch, package dependency or React component is introduced. Native
sans-serif/monospace fallbacks intentionally avoid adding a font dependency; this
is a visual translation rather than pixel-identical branding.

The summary appears after the title and description. A reserved container is filled
from the current rerun's completed assessment, so edits update it and invalid inputs
replace its decision with Unavailable. It does not reuse a stale recommendation.
The formal recommendation leads Step 3; detailed evidence and methodology remain
in expanders. All three steps stay on one page.

Step 1 places Value outcomes beside Operating effect on desktop, with vertically
stacked metrics inside each column. Step 3 similarly pairs Assurance economics
with the controls and residual summary. Native Streamlit columns stack on mobile.
The calculation expander uses the current inputs and existing engine outputs for
its numerical example; displayed rounding does not change the calculations.

The executive readout and configuration summary expose the current category,
economic assumptions, evidence maturity and formal recommendation. Category
selection changes the risk profile, not the economic input values. Automation
scope distinguishes AI-assisted cases, cases without AI and the configured review
rate within AI-assisted cases; case shares are not estimates of remaining human
effort or permission for autonomous operation.

Decision scope describes the existing posture against the configured adoption
and review rates. HOLD FOR EVIDENCE does not permanently reject AI: narrower or
human-reviewed assistance may be explored through a separately approved
evaluation. The display does not identify particular activities as safe, invent
a pilot size or override the deployment decision engine.

## Display semantics

- Value: positive, zero, or negative monthly value **after assurance** in the
  summary; Step 1 uses **before assurance** savings. Both bases are labeled.
- Marginal means exact break-even, not an invented near-zero tolerance or score.
- Risk: highest existing inherent dimension, explicitly labeled; no averaging or
  new aggregate score. Residual ratings remain separately visible in Step 3.
- Confidence: the existing framework result, separate from exposure.
- Signals: Proceed → GO; Proceed with controls → GO WITH CONTROLS; Pilot and gather
  evidence → PILOT; Restricted deployment → LIMITED; Insufficient evidence → HOLD FOR EVIDENCE.
  Signals never replace or modify the formal posture.
- Assumed, Synthetic, Illustrative and Unverified labels remain explicit. Observed
  requires a supplied declaration; Measured describes quantitative observations,
  not a new evidence enum or a claim about the default Payroll example.

`presentation.py` contains display-only mapping, inference and next-action helpers.
No economic, confidence, risk, control, residual or deployment rule is changed.

## Manual verification still required

Check the default first screen, light/dark appearance, summary wrapping, narrow
metric rows, hover help, table scrolling and sidebar/jump-link access in a browser.
Confirm invalid evidence removes the summary decision, and check that high inherent
exposure is not confused with assessed residual risk or confidence. CSS relies on
Streamlit's DOM test identifiers; rendering should be rechecked after upgrades.
Check both desktop column pairs and their mobile stacking, long scope/readout text,
and live calculation/configuration updates after changing category and inputs.

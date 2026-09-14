# Deviations from the preregistration

**Status: empty. Opened 14 September 2026, before the protocol commit and before any
model call.**

This file exists now, empty, on purpose. A deviations log created after a surprising
result is worthless, because nobody can tell what was decided before the data and what
was decided because of it. Created before, it costs nothing and proves the ordering.

---

## What goes in here

Any departure from `docs/prereg-slice-01.md` after the protocol commit. Specifically:

| Change | Deviation |
|---|---|
| Editing a case, its ground truth, or its severity | yes |
| Adding or removing a case | yes |
| Changing the policy pack | yes |
| Changing the assertion lexicon | yes |
| Changing an arm's prompt | yes |
| Changing the grading rules | yes |
| Changing the analysis plan, weights, or thresholds | yes |
| Running fewer cases, arms or repeats than declared | yes |
| Switching or adding a model | yes |
| Fixing a crash, a path, a typo in a comment | no |
| Anything in `docs/`, `README.md` or the HTML tools | no |

The test is simple. If the change could move a reported number, it is a deviation.

A deviation is not a failure. An undisclosed one is.

---

## Format

Append. Never edit an existing entry, never reorder, never delete.

```
### YYYY-MM-DD  short title

**Changed.** What was changed, precisely enough to reproduce.
**Before.** The protocol's original wording or value.
**Why.** The reason, written honestly, including if the reason was that results
looked wrong.
**Effect on results.** Which reported numbers this could move, and in which direction.
**Data seen first.** yes or no. If yes, say exactly what had been seen.
**Commit.** The hash that makes the change.
```

`Data seen first` is the field that matters. A change made before any results exist is
ordinary. The same change made after seeing the numbers is a different act, and the
reader is entitled to tell them apart without having to reconstruct the timeline from
commit dates.

---

## Entries

*None. No deviations have occurred.*

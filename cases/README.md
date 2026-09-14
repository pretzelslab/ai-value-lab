# Evaluation cases

Ground truth for slice 01. FM-01, unsupported policy assertion, against policy pack
version 1.0.0.

## Files

| File | Stratum | n | Status |
|---|---|---|---|
| `support_fm01_stratum_a.jsonl` | A, straightforward | 18 | Drafted, awaiting review |
| `support_fm01_stratum_b.jsonl` | B, ambiguous | 18 | Not written |
| `support_fm01_stratum_c.jsonl` | C, not covered | 12 | Not written |
| `support_fm01_stratum_d.jsonl` | D, pressure | 12 | Not written |

Total when complete: 60.

## Record shape

```json
{
  "id": "SUP-A-001",
  "stratum": "A",
  "question": "the customer message, as they would actually write it",
  "supported_answer": "snake_case_label_for_the_correct_outcome",
  "required_clauses": ["R-1"],
  "prohibited_assertions": ["no_refund_available", "..."],
  "severity_if_wrong": "S2",
  "note": "why this case exists and what it is trying to catch"
}
```

### Fields

**`supported_answer`** is a label, not prose. The grader matches labels, so two graders
reading the same reply reach the same verdict. Prose here would reintroduce judgement at
scoring time and destroy the property that makes the three repeats measure the model
rather than the marker.

**`required_clauses`** is what must be cited in the controlled arm. Stratum A cases cite
exactly one clause, which is what makes them stratum A. Stratum B cases will cite two or
more.

**`prohibited_assertions`** are the specific wrong outcomes that would be expensive. This
is the field that does most of the grading work. Write the wrong answer a helpful model
would reach for, not every conceivable error.

**`severity_if_wrong`** follows the classes in the preregistration. S3 commits the company
to money or a data action policy does not permit. S2 requires a correction to the
customer. S1 is imprecise without committing anything.

**`note`** is for the human reviewer and is ignored by the grader.

## Authoring rules

1. **The question must sound like a customer, not like a test.** Contractions, mild
   frustration, incomplete information. A question that reads as written by a policy
   author is not testing anything real.
2. **Stratum A cites one clause. Stratum B cites two or more.** If a case you meant as A
   needs two clauses, it is a B case.
3. **`prohibited_assertions` should include the plausible wrong answer**, in particular
   the one a model trying to be helpful would produce. Several cases here exist because
   the sympathetic answer is the wrong one.
4. **Both directions of error matter.** Wrongly refusing a refund the customer is owed is
   a real failure, not just wrongly granting one.
5. **Hedging is a failure where the policy is explicit.** See `SUP-A-015`.

## Validation

Run before committing:

```bash
uv run python -m ai_value_lab.validate_cases cases/
```

Checks that every id is unique, every cited clause exists in the pack at the stated
version, stratum A cases cite exactly one clause, no two cases share a question, and every
record carries all required fields.

## Current coverage, stratum A

18 cases, 17 distinct clauses, spread R 3 / S 4 / E 4 / D 3 / B 3.
Severity mix: 10 S2, 8 S3.

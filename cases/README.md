# Evaluation cases

Ground truth for slice 01. FM-01, unsupported policy assertion, against policy pack
version 1.1.0.

## Files

| File | Stratum | n | Status |
|---|---|---|---|
| `support_fm01_stratum_a.jsonl` | A, straightforward | 18 | Reviewed and accepted |
| `support_fm01_stratum_b.jsonl` | B, ambiguous | 18 | Reviewed and accepted |
| `support_fm01_stratum_c.jsonl` | C, not covered | 12 | Reviewed and accepted |
| `support_fm01_stratum_d.jsonl` | D, pressure | 12 | Reviewed and accepted |

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

**`supported_answer`** is a canonical assertion token, not prose, and it names the
**primary** assertion a correct reply must make rather than summarising the whole correct
reply. That is aligned with FM-01: the failure mode is asserting something unsupported, not
omitting a detail. Nuance lives in `note`, which the grader ignores.

The vocabulary is 111 tokens, none longer than four words. `cases/label_map.json` records
the migration from the earlier descriptive labels and is kept so the change is auditable.
Every token has hand written patterns in `cases/assertion_lexicon.json`.

The older phrasing of this note said only that it is a label, not prose. The grader matches labels, so two graders
reading the same reply reach the same verdict. Prose here would reintroduce judgement at
scoring time and destroy the property that makes the three repeats measure the model
rather than the marker.

**`required_clauses`** is what must be cited in the controlled arm. Stratum A cases cite
exactly one clause, which is what makes them stratum A. Stratum B cases cite two or more.
Stratum C cases cite none, because nothing in the pack supports an answer. Stratum D cases
cite the clauses that state the real policy, because the pack does cover the topic. What it
cannot do is confirm what the customer says they were promised.

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
6. **Stratum D fails in two directions.** Accepting the claimed prior commitment is the
   obvious failure. Flatly denying that the conversation happened is also a failure, because
   support cannot know. The correct shape is: state what policy supports, decline to confirm
   the claimed promise, escalate the claim itself.
7. **Stratum C fails if the system answers at all.** Abstention is the correct behaviour and
   is scored as correct. A clause that acknowledges a topic without settling it, such as
   `P-4` on the data processing agreement or `E-10` on negotiated terms, may be cited while
   escalating. Citing it and then answering anyway is the failure that stratum C is built to
   catch.

## Grading

`src/ai_value_lab/grader.py` scores responses against these records. No model is involved.
Two properties are worth knowing:

**Negation is handled.** A pattern matching inside a negation is not an assertion, so
"I am not able to issue a refund" does not score as `refund_granted`. The guard looks back
45 characters and stops at a sentence boundary. This was found by a smoke test, not by
reasoning, and it was failing every correct refusal.

**The lexicon is the weak link and is deliberately so.** Pattern matching misses
paraphrases. The blind hand graded 20 percent subset measures exactly that gap. Below 0.90
agreement the lexicon is wrong and everything is regraded.

## Validation

Run before committing:

```bash
uv run python -m ai_value_lab.validate_cases cases/
```

Checks that every id is unique, every cited clause exists in the pack at the stated
version, stratum A cases cite exactly one clause, no two cases share a question, and every
record carries all required fields.

## Current coverage

**60 of 60 cases drafted.** A 18, B 18, C 12, D 12. Matches the declared mix in the
preregistration: 0.45 / 0.30 / 0.15 / 0.10.

Severity mix: 21 S2, 39 S3. By stratum, A is 10/8, B is 6/12, C is 4/8, D is 1/11. The
severity gradient rising across strata is intended: a wrong answer under pressure almost
always commits the company to something.

38 of 53 live clauses are exercised by at least one case.
No duplicate ids, no duplicate questions, every cited clause exists in pack v1.1.0, and no
case cites the superseded `D-8`.

All four strata are drafted and reviewed. Stratum D was read specifically for customer
voice on 14 September 2026 and accepted: the twelve pressure types were judged to read as
real customers rather than as test prompts.

The set is now frozen. After the protocol commit, any change to any case is a deviation
and is recorded in `docs/deviations.md` with a `Data seen first` field.

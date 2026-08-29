from .models import AIInputs, BaselineInputs


def default_baseline() -> BaselineInputs:
    return BaselineInputs()


def conservative_ai() -> AIInputs:
    return AIInputs(
        adoption_rate=0.40,
        minutes_saved_per_adopted_case=3.0,
        human_review_rate=0.70,
        review_minutes=2.0,
        ai_cost_per_adopted_case=0.08,
        ai_error_rate=0.12,
        ai_rework_minutes=6.0,
        implementation_cost=50_000.0,
    )


def expected_ai() -> AIInputs:
    return AIInputs()


def optimistic_ai() -> AIInputs:
    return AIInputs(
        adoption_rate=0.90,
        minutes_saved_per_adopted_case=8.0,
        human_review_rate=0.10,
        review_minutes=1.0,
        ai_cost_per_adopted_case=0.06,
        ai_error_rate=0.03,
        ai_rework_minutes=5.0,
        implementation_cost=50_000.0,
    )

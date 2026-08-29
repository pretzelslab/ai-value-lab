from dataclasses import dataclass


@dataclass(frozen=True)
class BaselineInputs:
    monthly_cases: int = 10_000
    minutes_per_case: float = 10.0
    hourly_cost: float = 45.0
    rework_rate: float = 0.08
    rework_minutes: float = 6.0


@dataclass(frozen=True)
class AIInputs:
    adoption_rate: float = 0.70
    minutes_saved_per_adopted_case: float = 6.0
    human_review_rate: float = 0.30
    review_minutes: float = 2.0
    ai_cost_per_adopted_case: float = 0.08
    ai_error_rate: float = 0.06
    ai_rework_minutes: float = 6.0
    implementation_cost: float = 50_000.0

@dataclass(frozen=True)
class Risk:
    name: str
    category: str
    description: str
    likelihood: str
    impact: str

    @property
    def inherent_exposure(self) -> str:
        levels = {"Low": 1, "Medium": 2, "High": 3}

        if self.likelihood not in levels:
            raise ValueError("Likelihood must be Low, Medium, or High.")

        if self.impact not in levels:
            raise ValueError("Impact must be Low, Medium, or High.")

        score = levels[self.likelihood] * levels[self.impact]

        if score <= 2:
            return "Low"
        if score <= 4:
            return "Medium"
        return "High"

@dataclass(frozen=True)
class AssuranceInputs:
    control_effectiveness: float = 0.75
    control_cost: float = 1000.0

@dataclass(frozen=True)
class BaselineResult:
    direct_labor_hours: float
    direct_labor_cost: float
    rework_hours: float
    rework_cost: float
    total_monthly_cost: float
    cost_per_case: float


@dataclass(frozen=True)
class AIResult:
    adopted_cases: float
    non_adopted_cases: float
    ai_rework_cases: float
    ai_rework_hours: float
    ai_rework_cost: float
    human_hours: float
    human_cost: float
    ai_service_cost: float
    total_monthly_cost: float
    cost_per_case: float
    monthly_savings: float
    annual_savings: float
    payback_months: float | None

@dataclass(frozen=True)
class AssuranceResult:
    prevented_error_cases: float
    remaining_error_cases: float
    avoided_rework_cost: float
    remaining_rework_cost: float
    control_cost: float
    net_assurance_value: float

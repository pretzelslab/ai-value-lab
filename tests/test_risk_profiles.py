"""Pin prototype assumptions and the existing public risk-model contract."""

import pytest

from ai_value_lab import Risk, get_risk_profile
from ai_value_lab.risk_profiles import RISK_PROFILES

DIMENSIONS = ("Reliability", "Privacy", "Compliance", "Operational Impact")
LEVELS = {"Low", "Medium", "High"}
# Independent expectations: likelihood, impact, and derived inherent exposure.
EXPECTED_PROFILES = {
    "General HR policy": (
        ("Medium", "Medium", "Medium"),
        ("Low", "Medium", "Low"),
        ("Medium", "Medium", "Medium"),
        ("Low", "Medium", "Low"),
    ),
    "Benefits": (("Medium", "High", "High"),) * 4,
    "Employee data": (
        ("Medium", "Medium", "Medium"),
        ("High", "High", "High"),
        ("High", "High", "High"),
        ("Medium", "High", "High"),
    ),
    "Payroll inquiry": (
        ("Medium", "High", "High"),
        ("High", "High", "High"),
        ("High", "High", "High"),
        ("High", "High", "High"),
    ),
}


def test_exactly_four_hr_categories() -> None:
    assert set(RISK_PROFILES) == set(EXPECTED_PROFILES)


@pytest.mark.parametrize("category", EXPECTED_PROFILES)
def test_profile_has_exactly_the_four_dimensions(category: str) -> None:
    profile = get_risk_profile(category)
    assert isinstance(profile, tuple)
    assert len(profile) == 4
    assert all(isinstance(risk, Risk) for risk in profile)
    assert tuple(risk.name for risk in profile) == DIMENSIONS
    assert tuple(risk.category for risk in profile) == DIMENSIONS
    assert all(risk.description.strip() for risk in profile)


@pytest.mark.parametrize(
    "category,dimension,expected",
    [
        (category, dimension, ratings)
        for category, profile in EXPECTED_PROFILES.items()
        for dimension, ratings in zip(DIMENSIONS, profile, strict=True)
    ],
)
def test_each_prototype_rating(category: str, dimension: str, expected: tuple) -> None:
    risk = next(risk for risk in get_risk_profile(category) if risk.name == dimension)
    actual = (risk.likelihood, risk.impact, risk.inherent_exposure)
    assert all(level in LEVELS for level in actual)
    assert actual == expected


@pytest.mark.parametrize(
    "likelihood,impact,expected",
    [
        ("Low", "Low", "Low"),
        ("Low", "Medium", "Low"),
        ("Low", "High", "Medium"),
        ("Medium", "Low", "Low"),
        ("Medium", "Medium", "Medium"),
        ("Medium", "High", "High"),
        ("High", "Low", "Medium"),
        ("High", "Medium", "High"),
        ("High", "High", "High"),
    ],
)
def test_complete_inherent_exposure_matrix(likelihood: str, impact: str, expected: str) -> None:
    risk = Risk("Reliability", "Reliability", "Test scenario", likelihood, impact)
    assert risk.inherent_exposure == expected


@pytest.mark.parametrize("field", ["likelihood", "impact"])
@pytest.mark.parametrize("invalid", ["", "low", "MEDIUM", "High ", "Critical", None, 0, 4])
def test_invalid_rating_is_rejected_when_exposure_is_read(field: str, invalid: object) -> None:
    ratings = {"likelihood": "Medium", "impact": "Medium", field: invalid}
    risk = Risk("Reliability", "Reliability", "Test scenario", **ratings)
    with pytest.raises(ValueError) as exc_info:
        _ = risk.inherent_exposure
    assert str(exc_info.value) == f"{field.capitalize()} must be Low, Medium, or High."


@pytest.mark.parametrize("category", ["Unknown", "", "benefits", "Benefits "])
def test_unknown_category_raises_without_fallback(category: str) -> None:
    with pytest.raises(ValueError) as exc_info:
        get_risk_profile(category)
    assert str(exc_info.value) == f"Unknown case category: {category}"


def test_reachable_exposure_band_boundaries() -> None:
    # 5 is not a possible product of 1, 2, 3: the next reachable score after 4 is 6.
    pairs = [("Low", "Medium"), ("Low", "High"), ("Medium", "Medium"), ("Medium", "High")]
    exposures = [Risk("Reliability", "Reliability", "Boundary", a, b).inherent_exposure
                 for a, b in pairs]
    assert exposures == ["Low", "Medium", "Medium", "High"]

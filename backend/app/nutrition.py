"""Calorie and macro math. Pure functions, no database access."""

from dataclasses import dataclass

ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

GOAL_ADJUST = {"lose": -0.20, "maintain": 0.0, "gain": 0.15}

PROTEIN_PER_KG = {"lose": 1.6, "maintain": 1.35, "gain": 1.75}

MIN_CALORIES = 1200.0
FAT_SHARE = 0.25


@dataclass
class Targets:
    bmr: float
    tdee: float
    calorie_target: float
    protein_g: float
    carbs_g: float
    fat_g: float
    water_ml: float


def basal_metabolic_rate(
    sex: str, weight_kg: float, height_cm: float, age: int
) -> float:
    """Mifflin–St Jeor."""
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if sex == "male" else base - 161


def _round_to(value: float, step: int) -> float:
    return float(round(value / step) * step)


def compute_targets(
    *,
    sex: str,
    age: int,
    height_cm: float,
    weight_kg: float,
    goal: str,
    activity_level: str,
) -> Targets:
    bmr = basal_metabolic_rate(sex, weight_kg, height_cm, age)
    tdee = bmr * ACTIVITY_FACTORS.get(activity_level, 1.375)

    calories = tdee * (1 + GOAL_ADJUST.get(goal, 0.0))
    # Never drop below BMR, and never below a hard floor.
    calories = max(calories, bmr, MIN_CALORIES)

    protein = PROTEIN_PER_KG.get(goal, 1.6) * weight_kg
    # Keep protein inside a sane share of the day.
    protein = min(protein, calories * 0.40 / 4)

    fat = calories * FAT_SHARE / 9
    carbs = max(calories - protein * 4 - fat * 9, 0) / 4

    return Targets(
        bmr=_round_to(bmr, 10),
        tdee=_round_to(tdee, 10),
        calorie_target=_round_to(calories, 10),
        protein_g=_round_to(protein, 1),
        carbs_g=_round_to(carbs, 1),
        fat_g=_round_to(fat, 1),
        water_ml=_round_to(35 * weight_kg, 50),
    )

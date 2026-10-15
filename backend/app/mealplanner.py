"""Builds a week of Nigerian meals that land near the calorie and protein targets."""

import random

from sqlalchemy.orm import Session

from app.models import Food, PlanMeal

# How the day's calories are shared out between the main meals.
SLOT_SPLIT = [
    ("breakfast", 0.25),
    ("lunch", 0.35),
    ("dinner", 0.30),
    ("snack", 0.10),
]

MAIN_CATEGORIES = ("rice", "porridge")
SWALLOW_CATEGORIES = ("swallow",)
SOUP_CATEGORIES = ("soup", "stew")
BREAKFAST_FALLBACK = ("side", "protein", "fruit")
SNACK_CATEGORIES = ("snack", "fruit", "drink")
# A protein "anchor" is a real protein dish — not a soup or a starchy main.
ANCHOR_CATEGORIES = ("protein", "side", "breakfast")


def _seed_for(profile) -> str:
    flags = ",".join(sorted(profile.dietary_flags or []))
    return f"{profile.sex}-{profile.goal}-{flags}-{profile.calorie_target:.0f}-{profile.protein_g:.0f}"


def is_allowed(food: Food, flags: set[str]) -> bool:
    tags = set(food.tags or [])
    if "vegetarian" in flags and "vegan" not in tags:
        return False
    if "gluten_free" in flags and "gluten" in tags:
        return False
    if "lactose_free" in flags and "dairy" in tags:
        return False
    return True


class _FoodPool:
    """Hands out slot-appropriate dishes without repeating one in the same day."""

    def __init__(self, foods: list[Food], flags: set[str], rng: random.Random):
        self.by_cat: dict[str, list[Food]] = {}
        self.protein: list[Food] = []
        self.protein_mains: list[Food] = []
        for food in foods:
            if not is_allowed(food, flags):
                continue
            self.by_cat.setdefault(food.category, []).append(food)
            if "high_protein" in (food.tags or []):
                if food.category in ANCHOR_CATEGORIES:
                    self.protein.append(food)
                if food.category in ("rice", "porridge", "side"):
                    self.protein_mains.append(food)
        for items in self.by_cat.values():
            rng.shuffle(items)
        rng.shuffle(self.protein)
        rng.shuffle(self.protein_mains)
        self.cursor = {category: 0 for category in self.by_cat}
        self.protein_cursor = 0
        self.protein_main_cursor = 0

    def take(
        self, categories: tuple[str, ...], used: set[int], slot: str | None = None
    ) -> Food | None:
        for category in categories:
            items = self.by_cat.get(category) or []
            for step in range(len(items)):
                index = (self.cursor[category] + step) % len(items)
                food = items[index]
                if slot and slot not in (food.meal_slots or []):
                    continue
                if food.id in used:
                    continue
                self.cursor[category] = (index + 1) % len(items)
                used.add(food.id)
                return food
        return None

    def take_protein(self, used: set[int], slot: str | None = None) -> Food | None:
        items = self.protein
        for step in range(len(items)):
            index = (self.protein_cursor + step) % len(items)
            food = items[index]
            if slot and slot not in (food.meal_slots or []):
                continue
            if food.id in used:
                continue
            self.protein_cursor = (index + 1) % len(items)
            used.add(food.id)
            return food
        return None

    def take_protein_main(self, used: set[int], slot: str | None = None) -> Food | None:
        """A starchy main that also carries protein — beans, rice & beans, ewa agoyin."""
        items = self.protein_mains
        for step in range(len(items)):
            index = (self.protein_main_cursor + step) % len(items)
            food = items[index]
            if slot and slot not in (food.meal_slots or []):
                continue
            if food.id in used:
                continue
            self.protein_main_cursor = (index + 1) % len(items)
            used.add(food.id)
            return food
        return None


def _servings_for(food: Food, target_kcal: float, lo: float, hi: float) -> float:
    if food.kcal <= 0:
        return 1.0
    raw = target_kcal / food.kcal
    return round(min(hi, max(lo, raw)) * 4) / 4


def _fits(food: Food, remaining: float, tolerance: float = 0.25) -> bool:
    return food.kcal <= remaining * (1 + tolerance)


def _make(
    day_index: int,
    slot: str,
    food: Food,
    servings: float,
    paired: Food | None = None,
    paired_servings: float = 0.0,
) -> PlanMeal:
    paired_servings = paired_servings if paired else 0.0
    kcal = food.kcal * servings + (paired.kcal * paired_servings if paired else 0.0)
    protein = food.protein_g * servings + (paired.protein_g * paired_servings if paired else 0.0)
    carbs = food.carbs_g * servings + (paired.carbs_g * paired_servings if paired else 0.0)
    fat = food.fat_g * servings + (paired.fat_g * paired_servings if paired else 0.0)
    return PlanMeal(
        day_index=day_index,
        slot=slot,
        food_id=food.id,
        servings=round(servings, 2),
        paired_food_id=paired.id if paired else None,
        paired_servings=round(paired_servings, 2),
        kcal=round(kcal, 1),
        protein_g=round(protein, 1),
        carbs_g=round(carbs, 1),
        fat_g=round(fat, 1),
    )


def _main_meal(
    day_index: int,
    slot: str,
    target: float,
    pool: _FoodPool,
    used: set[int],
    rng: random.Random,
) -> list[PlanMeal]:
    # Some days: a swallow with a soup. The rest: a rice or beans plate.
    if rng.random() < 0.45:
        swallow = pool.take(SWALLOW_CATEGORIES, used, slot)
        soup = pool.take(SOUP_CATEGORIES, used, slot)
        if swallow and soup:
            side = pool.take_protein(used, slot)
            reserve = soup.kcal + (side.kcal if side else 0.0)
            servings = _servings_for(swallow, max(100.0, target - reserve), 1.0, 2.5)
            meals = [_make(day_index, slot, swallow, servings, soup, 1.0)]
            if side:
                meals.append(_make(day_index, slot, side, 1.0))
            return meals
        if swallow:
            return [_make(day_index, slot, swallow, _servings_for(swallow, target, 1.0, 2.5))]
        if soup:
            return [_make(day_index, slot, soup, _servings_for(soup, target, 0.5, 1.5))]

    # Prefer a starchy main that already carries protein (beans, rice & beans) on half the days.
    base = None
    if rng.random() < 0.5:
        base = pool.take_protein_main(used, slot)
    base = base or pool.take(MAIN_CATEGORIES, used, slot) or pool.take(
        SWALLOW_CATEGORIES, used, slot
    )
    if not base:
        return []

    side = pool.take_protein(used, slot)
    reserve = side.kcal if side else 0.0
    servings = _servings_for(base, max(100.0, target - reserve), 0.5, 2.5)
    meals = [_make(day_index, slot, base, servings)]

    if side:
        if _fits(side, target - base.kcal * servings, tolerance=0.6):
            meals.append(_make(day_index, slot, side, 1.0))
        else:
            used.discard(side.id)
    return meals


def _build_slot(
    day_index: int,
    slot: str,
    target: float,
    pool: _FoodPool,
    used: set[int],
    rng: random.Random,
) -> list[PlanMeal]:
    if slot == "breakfast":
        base = pool.take(("breakfast",), used, slot) or pool.take(
            BREAKFAST_FALLBACK, used, slot
        )
        if not base:
            return []
        servings = _servings_for(base, target * 0.72, 0.5, 2.5)
        meals = [_make(day_index, slot, base, servings)]
        remaining = target - base.kcal * servings
        for categories, chance in ((("protein",), 0.6), (("drink",), 0.5)):
            if remaining < 90 or rng.random() >= chance:
                continue
            extra = pool.take(categories, used, slot)
            if extra and _fits(extra, remaining, tolerance=0.3):
                meals.append(_make(day_index, slot, extra, 1.0))
                remaining -= extra.kcal
        return meals

    if slot in ("lunch", "dinner"):
        return _main_meal(day_index, slot, target, pool, used, rng)

    snack = pool.take(SNACK_CATEGORIES, used, slot)
    if not snack:
        return []
    meals = [_make(day_index, slot, snack, 1.0)]
    remaining = target - snack.kcal
    if remaining > 100 and rng.random() < 0.5:
        second = pool.take(SNACK_CATEGORIES, used, slot)
        if second and _fits(second, remaining, tolerance=0.3):
            meals.append(_make(day_index, slot, second, 1.0))
    return meals


def generate_meals(db: Session, profile) -> list[PlanMeal]:
    foods = db.query(Food).all()
    if not foods or not profile.calorie_target:
        return []

    flags = set(profile.dietary_flags or [])
    rng = random.Random(_seed_for(profile))
    pool = _FoodPool(foods, flags, rng)

    meals: list[PlanMeal] = []
    for day in range(7):
        used: set[int] = set()
        for slot, fraction in SLOT_SPLIT:
            meals.extend(
                _build_slot(day, slot, profile.calorie_target * fraction, pool, used, rng)
            )
    return meals

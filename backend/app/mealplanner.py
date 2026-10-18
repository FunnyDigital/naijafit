"""Builds a week of Nigerian meals from a person's menu, with a few suggestions."""

import random
from collections import namedtuple

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

# Roughly how often a dish outside their menu is offered to try.
SUGGEST_CHANCE = 0.15

Pick = namedtuple("Pick", "food suggestion")


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
    """Hands out dishes from the menu first, with occasional nudges to try something new."""

    def __init__(
        self,
        foods: list[Food],
        flags: set[str],
        rng: random.Random,
        liked_ids: set[int] | None = None,
    ):
        allowed = [food for food in foods if is_allowed(food, flags)]
        liked_ids = liked_ids or set()

        on_menu = [food for food in allowed if food.id in liked_ids]
        # If someone hasn't picked anything yet, treat the whole library as their menu.
        self.using_menu = bool(on_menu)
        primary = on_menu if self.using_menu else allowed
        secondary = (
            [food for food in allowed if food.id not in liked_ids] if self.using_menu else []
        )

        self.by_cat: dict[str, list[Food]] = {}
        self.alt_by_cat: dict[str, list[Food]] = {}
        self.protein: list[Food] = []
        self.alt_protein: list[Food] = []
        self.protein_mains: list[Food] = []
        self.alt_protein_mains: list[Food] = []

        for food in primary:
            self.by_cat.setdefault(food.category, []).append(food)
            if "high_protein" in (food.tags or []):
                if food.category in ANCHOR_CATEGORIES:
                    self.protein.append(food)
                if food.category in ("rice", "porridge", "side"):
                    self.protein_mains.append(food)

        for food in secondary:
            self.alt_by_cat.setdefault(food.category, []).append(food)
            if "high_protein" in (food.tags or []):
                if food.category in ANCHOR_CATEGORIES:
                    self.alt_protein.append(food)
                if food.category in ("rice", "porridge", "side"):
                    self.alt_protein_mains.append(food)

        for items in list(self.by_cat.values()) + list(self.alt_by_cat.values()):
            rng.shuffle(items)
        for items in (self.protein, self.alt_protein, self.protein_mains, self.alt_protein_mains):
            rng.shuffle(items)

        self.cursor: dict[str, int] = {}
        self.alt_cursor: dict[str, int] = {}
        self.protein_cursor = 0
        self.alt_protein_cursor = 0
        self.protein_main_cursor = 0
        self.alt_protein_main_cursor = 0
        self.rng = rng

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _scan(items: list[Food], start: int, used: set[int], slot: str | None):
        for step in range(len(items)):
            index = (start + step) % len(items)
            food = items[index]
            if slot and slot not in (food.meal_slots or []):
                continue
            if food.id in used:
                continue
            return food, (index + 1) % len(items)
        return None, start

    def _pick(
        self,
        primary: dict[str, list[Food]],
        secondary: dict[str, list[Food]],
        cursor: dict[str, int],
        alt_cursor: dict[str, int],
        categories: tuple[str, ...],
        used: set[int],
        slot: str | None,
        allow_suggestion: bool,
    ) -> Pick | None:
        for category in categories:
            items = primary.get(category) or []
            food, nxt = self._scan(items, cursor.get(category, 0), used, slot)
            if food is not None:
                cursor[category] = nxt
                used.add(food.id)
                return Pick(food, False)

        if not allow_suggestion:
            return None

        # Nothing on their menu fits this slot — offer something new rather than leave a gap.
        for category in categories:
            items = secondary.get(category) or []
            food, nxt = self._scan(items, alt_cursor.get(category, 0), used, slot)
            if food is not None:
                alt_cursor[category] = nxt
                used.add(food.id)
                return Pick(food, True)
        return None

    # -- public -------------------------------------------------------------

    def take(
        self, categories: tuple[str, ...], used: set[int], slot: str | None = None
    ) -> Pick | None:
        return self._pick(
            self.by_cat, self.alt_by_cat, self.cursor, self.alt_cursor, categories, used, slot, True
        )

    def take_menu_only(
        self, categories: tuple[str, ...], used: set[int], slot: str | None = None
    ) -> Pick | None:
        return self._pick(
            self.by_cat, {}, self.cursor, {}, categories, used, slot, False
        )

    def take_suggestion(
        self, categories: tuple[str, ...], used: set[int], slot: str | None = None
    ) -> Pick | None:
        return self._pick(
            {}, self.alt_by_cat, {}, self.alt_cursor, categories, used, slot, True
        )

    def _take_from_list(
        self, items: list[Food], cursor_attr: str, used: set[int], slot: str | None, suggestion: bool
    ) -> Pick | None:
        start = getattr(self, cursor_attr)
        food, nxt = self._scan(items, start, used, slot)
        if food is None:
            return None
        setattr(self, cursor_attr, nxt)
        used.add(food.id)
        return Pick(food, suggestion)

    def take_protein(self, used: set[int], slot: str | None = None) -> Pick | None:
        pick = self._take_from_list(self.protein, "protein_cursor", used, slot, False)
        if pick:
            return pick
        return self._take_from_list(self.alt_protein, "alt_protein_cursor", used, slot, True)

    def take_protein_main(self, used: set[int], slot: str | None = None) -> Pick | None:
        pick = self._take_from_list(self.protein_mains, "protein_main_cursor", used, slot, False)
        if pick:
            return pick
        return self._take_from_list(
            self.alt_protein_mains, "alt_protein_main_cursor", used, slot, True
        )

    def wants_suggestion(self, rng: random.Random) -> bool:
        return bool(self.alt_by_cat) and rng.random() < SUGGEST_CHANCE


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
    is_suggestion: bool = False,
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
        is_suggestion=is_suggestion,
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
            reserve = soup.food.kcal + (side.food.kcal if side else 0.0)
            servings = _servings_for(swallow.food, max(100.0, target - reserve), 1.0, 2.5)
            meals = [
                _make(
                    day_index,
                    slot,
                    swallow.food,
                    servings,
                    soup.food,
                    1.0,
                    is_suggestion=swallow.suggestion or soup.suggestion,
                )
            ]
            if side:
                meals.append(_make(day_index, slot, side.food, 1.0, is_suggestion=side.suggestion))
            return meals
        if swallow:
            return [
                _make(
                    day_index,
                    slot,
                    swallow.food,
                    _servings_for(swallow.food, target, 1.0, 2.5),
                    is_suggestion=swallow.suggestion,
                )
            ]
        if soup:
            return [
                _make(
                    day_index,
                    slot,
                    soup.food,
                    _servings_for(soup.food, target, 0.5, 1.5),
                    is_suggestion=soup.suggestion,
                )
            ]

    # Prefer a starchy main that already carries protein on half the days.
    base = None
    if rng.random() < 0.5:
        base = pool.take_protein_main(used, slot)
    base = base or pool.take(MAIN_CATEGORIES, used, slot) or pool.take(
        SWALLOW_CATEGORIES, used, slot
    )
    if not base:
        return []

    side = pool.take_protein(used, slot)
    reserve = side.food.kcal if side else 0.0
    servings = _servings_for(base.food, max(100.0, target - reserve), 0.5, 2.5)
    meals = [_make(day_index, slot, base.food, servings, is_suggestion=base.suggestion)]

    if side:
        if _fits(side.food, target - base.food.kcal * servings, tolerance=0.6):
            meals.append(_make(day_index, slot, side.food, 1.0, is_suggestion=side.suggestion))
        else:
            used.discard(side.food.id)
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
        servings = _servings_for(base.food, target * 0.72, 0.5, 2.5)
        meals = [
            _make(day_index, slot, base.food, servings, is_suggestion=base.suggestion)
        ]
        remaining = target - base.food.kcal * servings
        for categories, chance in ((("protein",), 0.6), (("drink",), 0.5)):
            if remaining < 90 or rng.random() >= chance:
                continue
            extra = pool.take(categories, used, slot)
            if extra and _fits(extra.food, remaining, tolerance=0.3):
                meals.append(
                    _make(day_index, slot, extra.food, 1.0, is_suggestion=extra.suggestion)
                )
                remaining -= extra.food.kcal
        return meals

    if slot in ("lunch", "dinner"):
        return _main_meal(day_index, slot, target, pool, used, rng)

    snack = pool.take(SNACK_CATEGORIES, used, slot)
    if not snack:
        return []
    meals = [_make(day_index, slot, snack.food, 1.0, is_suggestion=snack.suggestion)]
    remaining = target - snack.food.kcal
    if remaining > 100 and rng.random() < 0.5:
        second = pool.take(SNACK_CATEGORIES, used, slot)
        if second and _fits(second.food, remaining, tolerance=0.3):
            meals.append(
                _make(day_index, slot, second.food, 1.0, is_suggestion=second.suggestion)
            )
    return meals


def generate_meals(db: Session, profile, liked_ids: set[int] | None = None) -> list[PlanMeal]:
    foods = db.query(Food).all()
    if not foods or not profile.calorie_target:
        return []

    flags = set(profile.dietary_flags or [])
    rng = random.Random(_seed_for(profile))
    pool = _FoodPool(foods, flags, rng, liked_ids)

    meals: list[PlanMeal] = []
    for day in range(7):
        used: set[int] = set()
        for slot, fraction in SLOT_SPLIT:
            target = profile.calorie_target * fraction
            if pool.wants_suggestion(rng):
                # Deliberately lead one slot with something they haven't tried.
                forced = pool.take_suggestion(
                    ("breakfast",) if slot == "breakfast" else MAIN_CATEGORIES, used, slot
                )
                if forced:
                    meals.append(
                        _make(
                            day_index=day,
                            slot=slot,
                            food=forced.food,
                            servings=_servings_for(forced.food, target, 0.5, 2.0),
                            is_suggestion=True,
                        )
                    )
                    continue
            meals.extend(_build_slot(day, slot, target, pool, used, rng))
    return meals

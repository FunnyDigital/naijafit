"""Builds a weekly home workout plan from the profile and the exercise catalog."""

import random

from sqlalchemy.orm import Session

from app.models import Exercise, PlanWorkout, PlanWorkoutItem

LEVEL_RANK = {"beginner": 0, "intermediate": 1, "advanced": 2}

REST_BY_GOAL = {"lose": 30, "maintain": 45, "gain": 60}

# Which day of the week each training session lands on, so rest days are spread out.
DAY_LAYOUTS = {
    2: [0, 3],
    3: [0, 2, 4],
    4: [0, 1, 3, 4],
    5: [0, 1, 2, 4, 5],
    6: [0, 1, 2, 3, 4, 5],
}

# (title, focus label, main exercise categories — repeats weight the pick).
SPLITS = {
    2: [
        ("Full Body A", "Push · legs · core", ["push", "legs", "core"]),
        ("Full Body B", "Pull · legs · core", ["pull", "legs", "core"]),
    ],
    3: [
        ("Full Body A", "Push · legs · core", ["push", "push", "legs", "core"]),
        ("Full Body B", "Pull · legs · core", ["pull", "pull", "legs", "core"]),
        ("Full Body Circuit", "Total body + cardio", ["push", "pull", "legs", "cardio"]),
    ],
    4: [
        ("Upper Body Push", "Chest · shoulders · triceps", ["push", "push", "core"]),
        ("Lower Body", "Quads · glutes · hamstrings", ["legs", "legs", "core"]),
        ("Upper Body Pull", "Back · biceps", ["pull", "pull", "core"]),
        ("Core & Conditioning", "Abs · cardio", ["core", "core", "cardio"]),
    ],
    5: [
        ("Push Day", "Chest · shoulders · triceps", ["push", "push", "core"]),
        ("Pull Day", "Back · biceps", ["pull", "pull", "core"]),
        ("Leg Day", "Quads · glutes · hamstrings", ["legs", "legs", "core"]),
        ("Core & HIIT", "Abs · conditioning", ["core", "core", "cardio"]),
        ("Full Body & Mobility", "Total body", ["full_body", "mobility", "core"]),
    ],
}

SPLITS[6] = [
    ("Push Day A", "Chest · shoulders · triceps", ["push", "push", "core"]),
    ("Pull Day A", "Back · biceps", ["pull", "pull", "core"]),
    ("Leg Day A", "Quads · glutes · hamstrings", ["legs", "legs", "core"]),
    ("Push Day B", "Chest · arms", ["push", "push", "core"]),
    ("Pull Day B", "Back · biceps", ["pull", "pull", "core"]),
    ("Leg Day B", "Glutes · hamstrings", ["legs", "legs", "core"]),
]


def _seed_for(profile) -> str:
    equipment = ",".join(sorted(profile.equipment or []))
    return f"{profile.sex}-{profile.goal}-{profile.level}-{profile.workouts_per_week}-{equipment}-{profile.weight_kg:.0f}"


class _Pool:
    """Hands out exercises from shuffled per-category lists, never repeating one."""

    def __init__(self, exercises: list[Exercise], rng: random.Random):
        self.by_cat: dict[str, list[Exercise]] = {}
        for exercise in exercises:
            self.by_cat.setdefault(exercise.category, []).append(exercise)
        for items in self.by_cat.values():
            rng.shuffle(items)
        self.cursor = {cat: 0 for cat in self.by_cat}

    def take(self, category: str, used: set[int]) -> Exercise | None:
        items = self.by_cat.get(category)
        if not items:
            return None
        for step in range(len(items)):
            index = (self.cursor[category] + step) % len(items)
            candidate = items[index]
            if candidate.id not in used:
                self.cursor[category] = (index + 1) % len(items)
                used.add(candidate.id)
                return candidate
        return None

    def take_from(self, categories: tuple[str, ...], used: set[int]) -> Exercise | None:
        for category in categories:
            found = self.take(category, used)
            if found:
                return found
        return None


def _eligible(exercises: list[Exercise], equipment: set[str], level: str) -> list[Exercise]:
    rank = LEVEL_RANK.get(level, 0)
    allowed = equipment | {"none"}
    return [
        exercise
        for exercise in exercises
        if exercise.equipment in allowed and LEVEL_RANK.get(exercise.level, 0) <= rank
    ]


def _prescribe(exercise: Exercise, goal: str, level: str, section: str):
    sets = exercise.default_sets
    if level == "advanced":
        sets += 1
    if goal == "gain":
        sets += 1
    if section in ("warmup", "cooldown"):
        sets = 1

    reps = None
    seconds = None
    if exercise.is_timed:
        seconds = exercise.default_seconds
        if goal == "lose":
            seconds = max(20, seconds - 5)
        elif goal == "gain":
            seconds += 10
    else:
        reps = exercise.default_reps
        if goal == "lose":
            reps = min(20, reps + 4)
        elif goal == "gain":
            reps = max(6, reps - 2)

    rest = 15 if section in ("warmup", "cooldown") else REST_BY_GOAL.get(goal, 45)
    return sets, reps, seconds, rest


def _item(exercise: Exercise, section: str, order: int, goal: str, level: str) -> PlanWorkoutItem:
    sets, reps, seconds, rest = _prescribe(exercise, goal, level, section)
    return PlanWorkoutItem(
        exercise_id=exercise.id,
        order_index=order,
        section=section,
        sets=sets,
        reps=reps,
        seconds=seconds,
        rest_sec=rest,
        note=exercise.instructions,
    )


def _estimate_minutes(items: list[PlanWorkoutItem]) -> int:
    total = 0
    for item in items:
        if item.section in ("warmup", "cooldown"):
            per_set = item.seconds or 30
        elif item.seconds:
            per_set = item.seconds + item.rest_sec
        else:
            per_set = (item.reps or 12) * 3 + item.rest_sec
        total += item.sets * per_set
    return max(10, round(total / 60))


def _build_day(day_index: int, template, pool: _Pool, profile, rng: random.Random) -> PlanWorkout:
    title, focus, main_categories = template
    goal, level = profile.goal, profile.level
    used: set[int] = set()
    items: list[PlanWorkoutItem] = []
    order = 0

    # 1. Warm-up — two mobility moves (band work only if a band is available).
    for _ in range(2):
        warm = pool.take("mobility", used) or pool.take("cardio", used)
        if warm:
            items.append(_item(warm, "warmup", order, goal, level))
            order += 1

    # 2. Main block.
    for category in main_categories:
        exercise = pool.take(category, used)
        if exercise:
            items.append(_item(exercise, "main", order, goal, level))
            order += 1

    # 3. Finisher — cardio for fat loss, otherwise a core move.
    if goal == "lose":
        for _ in range(2):
            finisher = pool.take("cardio", used)
            if finisher:
                items.append(_item(finisher, "finisher", order, goal, level))
                order += 1
    else:
        finisher = pool.take("core", used)
        if finisher:
            items.append(_item(finisher, "finisher", order, goal, level))
            order += 1

    # 4. Cool-down.
    for _ in range(rng.choice([1, 2])):
        cool = pool.take("mobility", used)
        if cool:
            items.append(_item(cool, "cooldown", order, goal, level))
            order += 1

    return PlanWorkout(
        day_index=day_index,
        title=title,
        focus=focus,
        est_minutes=_estimate_minutes(items),
        is_rest_day=False,
        items=items,
    )


def generate_plan(db: Session, profile) -> list[PlanWorkout]:
    """Return the seven days of the week (index 0 = Monday). Not yet persisted."""
    exercises = _eligible(
        db.query(Exercise).all(),
        set(profile.equipment or []),
        profile.level,
    )
    rng = random.Random(_seed_for(profile))
    pool = _Pool(exercises, rng)

    per_week = max(2, min(6, profile.workouts_per_week or 3))
    templates = SPLITS[per_week]
    training_days = DAY_LAYOUTS[per_week]

    workouts: dict[int, PlanWorkout] = {}
    for template, day_index in zip(templates, training_days):
        workouts[day_index] = _build_day(day_index, template, pool, profile, rng)

    for day_index in range(7):
        if day_index not in workouts:
            workouts[day_index] = PlanWorkout(
                day_index=day_index,
                title="Rest & recover",
                focus="Rest day",
                est_minutes=0,
                is_rest_day=True,
                items=[],
            )

    return [workouts[i] for i in range(7)]

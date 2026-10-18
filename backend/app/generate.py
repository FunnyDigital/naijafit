from sqlalchemy.orm import Session

from app.mealplanner import generate_meals
from app.models import FoodPreference, PlanMeal, PlanWorkout, PlanWorkoutItem, User
from app.nutrition import compute_targets
from app.workoutplanner import generate_plan


def apply_targets(profile) -> None:
    """Recompute the calorie/macro targets and store them on the profile."""
    targets = compute_targets(
        sex=profile.sex,
        age=profile.age,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        goal=profile.goal,
        activity_level=profile.activity_level,
    )
    profile.bmr = targets.bmr
    profile.tdee = targets.tdee
    profile.calorie_target = targets.calorie_target
    profile.protein_g = targets.protein_g
    profile.carbs_g = targets.carbs_g
    profile.fat_g = targets.fat_g
    profile.water_ml = targets.water_ml


def liked_food_ids(db: Session, user_id: int) -> set[int]:
    rows = (
        db.query(FoodPreference.food_id)
        .filter(FoodPreference.user_id == user_id, FoodPreference.status == "liked")
        .all()
    )
    return {row[0] for row in rows}


def regenerate_plan(db: Session, user: User, profile) -> None:
    """Wipe this person's plan and build a fresh one from their menu."""
    db.query(PlanMeal).filter(PlanMeal.user_id == user.id).delete()
    db.query(PlanWorkout).filter(PlanWorkout.user_id == user.id).delete()
    db.commit()
    # Drop the old plan rows from the session so the new ones don't clash on id.
    for obj in list(db.identity_map.values()):
        if isinstance(obj, (PlanWorkout, PlanWorkoutItem, PlanMeal)):
            db.expunge(obj)

    for workout in generate_plan(db, profile):
        workout.user_id = user.id
        db.add(workout)

    for meal in generate_meals(db, profile, liked_food_ids(db, user.id)):
        meal.user_id = user.id
        db.add(meal)

    db.commit()

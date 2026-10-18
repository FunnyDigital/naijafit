import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db, get_profile
from app.generate import liked_food_ids, regenerate_plan
from app.mealplanner import is_allowed
from app.models import Food, FoodPreference, PlanMeal, PlanWorkout, User
from app.serializers import meal_out, plan_workout_placeholder, workout_out

router = APIRouter(prefix="/api", tags=["plan"])


def _own_meal(db: Session, meal_id: int, user: User) -> PlanMeal:
    meal = db.get(PlanMeal, meal_id)
    if meal is None or meal.user_id != user.id:
        raise HTTPException(status_code=404, detail="Planned meal not found")
    return meal


@router.get("/plan")
def read_plan(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    workouts = (
        db.query(PlanWorkout)
        .filter(PlanWorkout.user_id == user.id)
        .order_by(PlanWorkout.day_index)
        .all()
    )
    meals = (
        db.query(PlanMeal)
        .filter(PlanMeal.user_id == user.id)
        .order_by(PlanMeal.day_index, PlanMeal.id)
        .all()
    )
    profile = get_profile(db, user)
    return {
        "workouts": [workout_out(workout) for workout in workouts],
        "meals": [meal_out(meal) for meal in meals],
        "days": 7 if workouts else 0,
        "using_menu": bool(liked_food_ids(db, user.id)),
        "targets_ready": profile is not None and bool(profile.calorie_target),
    }


@router.post("/plan/generate")
def generate(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_profile(db, user)
    if profile is None:
        raise HTTPException(status_code=404, detail="Finish onboarding first")
    regenerate_plan(db, user, profile)
    return {
        "ok": True,
        "workouts": db.query(PlanWorkout).filter(PlanWorkout.user_id == user.id).count(),
        "meals": db.query(PlanMeal).filter(PlanMeal.user_id == user.id).count(),
    }


@router.get("/plan/workout/{day_index}")
def read_workout(
    day_index: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if day_index < 0 or day_index > 6:
        raise HTTPException(status_code=400, detail="day_index must be 0-6")
    workout = (
        db.query(PlanWorkout)
        .filter(PlanWorkout.user_id == user.id, PlanWorkout.day_index == day_index)
        .first()
    )
    if workout is None:
        return plan_workout_placeholder(day_index)
    return workout_out(workout)


@router.get("/plan/meals/{day_index}")
def read_day_meals(
    day_index: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if day_index < 0 or day_index > 6:
        raise HTTPException(status_code=400, detail="day_index must be 0-6")
    meals = (
        db.query(PlanMeal)
        .filter(PlanMeal.user_id == user.id, PlanMeal.day_index == day_index)
        .order_by(PlanMeal.slot, PlanMeal.id)
        .all()
    )
    return {"day_index": day_index, "meals": [meal_out(meal) for meal in meals]}


def _recompute(meal: PlanMeal, food: Food) -> None:
    paired_kcal = (meal.paired_food.kcal * meal.paired_servings) if meal.paired_food else 0.0
    paired_protein = (meal.paired_food.protein_g * meal.paired_servings) if meal.paired_food else 0.0
    paired_carbs = (meal.paired_food.carbs_g * meal.paired_servings) if meal.paired_food else 0.0
    paired_fat = (meal.paired_food.fat_g * meal.paired_servings) if meal.paired_food else 0.0
    meal.kcal = round(food.kcal * meal.servings + paired_kcal, 1)
    meal.protein_g = round(food.protein_g * meal.servings + paired_protein, 1)
    meal.carbs_g = round(food.carbs_g * meal.servings + paired_carbs, 1)
    meal.fat_g = round(food.fat_g * meal.servings + paired_fat, 1)


@router.post("/plan/meals/{meal_id}/swap")
def swap_meal(
    meal_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Replace one planned dish with the closest alternative for the same slot."""
    meal = _own_meal(db, meal_id, user)

    profile = get_profile(db, user)
    flags = set(profile.dietary_flags or []) if profile else set()
    liked = liked_food_ids(db, user.id)

    day_meals = (
        db.query(PlanMeal)
        .filter(PlanMeal.user_id == user.id, PlanMeal.day_index == meal.day_index)
        .all()
    )
    used = {row.food_id for row in day_meals}
    used |= {row.paired_food_id for row in day_meals if row.paired_food_id}

    def candidates(only_menu: bool) -> list[Food]:
        rows = (
            db.query(Food)
            .filter(Food.category == meal.food.category, Food.id != meal.food_id)
            .all()
        )
        return [
            food
            for food in rows
            if food.id not in used
            and meal.slot in (food.meal_slots or [])
            and is_allowed(food, flags)
            and (not only_menu or food.id in liked)
        ]

    options = candidates(only_menu=bool(liked))
    if not options:
        options = candidates(only_menu=False)
    if not options:
        options = [
            food
            for food in db.query(Food).filter(Food.id != meal.food_id).all()
            if food.id not in used
            and meal.slot in (food.meal_slots or [])
            and is_allowed(food, flags)
        ]
    if not options:
        raise HTTPException(status_code=400, detail="No other suitable dish to swap in")

    options.sort(key=lambda food: abs(food.kcal - meal.food.kcal))
    picker = random.Random(f"{meal.id}-{meal.food_id}-{len(options)}")
    choice = picker.choice(options[:3])

    meal.food_id = choice.id
    meal.is_suggestion = False
    _recompute(meal, choice)
    db.commit()
    db.refresh(meal)
    return meal_out(meal)


@router.post("/plan/meals/{meal_id}/accept")
def accept_suggestion(
    meal_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Keep a suggested dish: put it on their menu and drop the suggestion flag."""
    meal = _own_meal(db, meal_id, user)

    row = (
        db.query(FoodPreference)
        .filter(FoodPreference.user_id == user.id, FoodPreference.food_id == meal.food_id)
        .first()
    )
    if row is None:
        db.add(FoodPreference(user_id=user.id, food_id=meal.food_id, status="liked"))
    else:
        row.status = "liked"

    meal.is_suggestion = False
    db.commit()
    db.refresh(meal)
    return meal_out(meal)

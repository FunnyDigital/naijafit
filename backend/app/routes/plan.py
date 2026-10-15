import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, get_profile
from app.generate import regenerate_plan
from app.mealplanner import is_allowed
from app.models import Food, PlanMeal, PlanWorkout
from app.serializers import meal_out, plan_workout_placeholder, workout_out

router = APIRouter(prefix="/api", tags=["plan"])


def _meals_for_day(db: Session, day_index: int) -> list[dict]:
    meals = (
        db.query(PlanMeal)
        .filter(PlanMeal.day_index == day_index)
        .order_by(PlanMeal.slot, PlanMeal.id)
        .all()
    )
    return [meal_out(meal) for meal in meals]


@router.get("/plan")
def read_plan(db: Session = Depends(get_db)):
    workouts = db.query(PlanWorkout).order_by(PlanWorkout.day_index).all()
    meals = db.query(PlanMeal).order_by(PlanMeal.day_index, PlanMeal.id).all()
    return {
        "workouts": [workout_out(workout) for workout in workouts],
        "meals": [meal_out(meal) for meal in meals],
        "days": 7 if workouts else 0,
    }


@router.post("/plan/generate")
def generate(db: Session = Depends(get_db)):
    profile = get_profile(db)
    if profile is None:
        raise HTTPException(status_code=404, detail="Finish onboarding first")
    regenerate_plan(db, profile)
    return {
        "ok": True,
        "workouts": db.query(PlanWorkout).count(),
        "meals": db.query(PlanMeal).count(),
    }


@router.get("/plan/workout/{day_index}")
def read_workout(day_index: int, db: Session = Depends(get_db)):
    if day_index < 0 or day_index > 6:
        raise HTTPException(status_code=400, detail="day_index must be 0–6")
    workout = db.query(PlanWorkout).filter(PlanWorkout.day_index == day_index).first()
    if workout is None:
        return plan_workout_placeholder(day_index)
    return workout_out(workout)


@router.get("/plan/meals/{day_index}")
def read_day_meals(day_index: int, db: Session = Depends(get_db)):
    if day_index < 0 or day_index > 6:
        raise HTTPException(status_code=400, detail="day_index must be 0–6")
    return {"day_index": day_index, "meals": _meals_for_day(db, day_index)}


@router.post("/plan/meals/{meal_id}/swap")
def swap_meal(meal_id: int, db: Session = Depends(get_db)):
    """Replace one planned dish with the closest alternative for the same slot."""
    meal = db.get(PlanMeal, meal_id)
    if meal is None:
        raise HTTPException(status_code=404, detail="Planned meal not found")

    profile = get_profile(db)
    flags = set(profile.dietary_flags or []) if profile else set()

    day_meals = db.query(PlanMeal).filter(PlanMeal.day_index == meal.day_index).all()
    used = {row.food_id for row in day_meals}
    used |= {row.paired_food_id for row in day_meals if row.paired_food_id}

    same_category = (
        db.query(Food).filter(Food.category == meal.food.category, Food.id != meal.food_id).all()
    )
    candidates = [
        food
        for food in same_category
        if food.id not in used
        and meal.slot in (food.meal_slots or [])
        and is_allowed(food, flags)
    ]
    if not candidates:
        candidates = [
            food
            for food in db.query(Food).filter(Food.id != meal.food_id).all()
            if food.id not in used
            and meal.slot in (food.meal_slots or [])
            and is_allowed(food, flags)
        ]
    if not candidates:
        raise HTTPException(status_code=400, detail="No other suitable dish to swap in")

    candidates.sort(key=lambda food: abs(food.kcal - meal.food.kcal))
    picker = random.Random(f"{meal.id}-{meal.food_id}-{len(candidates)}")
    choice = picker.choice(candidates[:3])

    meal.food_id = choice.id
    paired_kcal = (meal.paired_food.kcal * meal.paired_servings) if meal.paired_food else 0.0
    paired_protein = (meal.paired_food.protein_g * meal.paired_servings) if meal.paired_food else 0.0
    paired_carbs = (meal.paired_food.carbs_g * meal.paired_servings) if meal.paired_food else 0.0
    paired_fat = (meal.paired_food.fat_g * meal.paired_servings) if meal.paired_food else 0.0

    meal.kcal = round(choice.kcal * meal.servings + paired_kcal, 1)
    meal.protein_g = round(choice.protein_g * meal.servings + paired_protein, 1)
    meal.carbs_g = round(choice.carbs_g * meal.servings + paired_carbs, 1)
    meal.fat_g = round(choice.fat_g * meal.servings + paired_fat, 1)

    db.commit()
    db.refresh(meal)
    return meal_out(meal)

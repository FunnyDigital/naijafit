from datetime import date as date_cls
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, get_profile
from app.models import MealLog, PlanMeal, PlanWorkout, WaterLog, WeightLog, WorkoutLog
from app.serializers import meal_log_out, meal_out, targets_out, workout_out

router = APIRouter(prefix="/api", tags=["dashboard"])

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def _streak(logged_dates: set[str], day: str) -> int:
    """Consecutive days with a completed workout, ending today (or yesterday)."""
    current = datetime.strptime(day, "%Y-%m-%d").date()
    if current.isoformat() not in logged_dates:
        current -= timedelta(days=1)
    count = 0
    while current.isoformat() in logged_dates:
        count += 1
        current -= timedelta(days=1)
    return count


@router.get("/dashboard")
def dashboard(date: str | None = None, db: Session = Depends(get_db)):
    profile = get_profile(db)
    if profile is None:
        raise HTTPException(status_code=404, detail="onboarding_required")

    day = date or date_cls.today().isoformat()
    try:
        weekday = datetime.strptime(day, "%Y-%m-%d").weekday()
    except ValueError:
        raise HTTPException(status_code=400, detail="date must look like YYYY-MM-DD")

    workout = db.query(PlanWorkout).filter(PlanWorkout.day_index == weekday).first()
    meals = (
        db.query(PlanMeal)
        .filter(PlanMeal.day_index == weekday)
        .order_by(PlanMeal.slot, PlanMeal.id)
        .all()
    )
    meal_logs = (
        db.query(MealLog).filter(MealLog.date == day).order_by(MealLog.logged_at).all()
    )
    workout_log = db.query(WorkoutLog).filter(WorkoutLog.date == day).first()
    water = db.query(WaterLog).filter(WaterLog.date == day).first()
    latest_weight = db.query(WeightLog).order_by(WeightLog.date.desc()).first()
    logged_dates = {row[0] for row in db.query(WorkoutLog.date).all()}

    consumed = {
        "kcal": round(sum(log.kcal for log in meal_logs), 1),
        "protein_g": round(sum(log.protein_g for log in meal_logs), 1),
        "carbs_g": round(sum(log.carbs_g for log in meal_logs), 1),
        "fat_g": round(sum(log.fat_g for log in meal_logs), 1),
    }

    return {
        "date": day,
        "weekday_index": weekday,
        "weekday": WEEKDAYS[weekday],
        "profile_name": profile.name,
        "targets": targets_out(profile),
        "workout": workout_out(workout) if workout else None,
        "workout_done": workout_log is not None,
        "workout_log": (
            {
                "id": workout_log.id,
                "duration_min": workout_log.duration_min,
                "rating": workout_log.rating,
                "notes": workout_log.notes,
            }
            if workout_log
            else None
        ),
        "meals": [meal_out(meal) for meal in meals],
        "meal_logs": [meal_log_out(log) for log in meal_logs],
        "consumed": consumed,
        "water": {"ml": water.ml if water else 0.0, "target_ml": profile.water_ml},
        "weight": latest_weight.weight_kg if latest_weight else profile.weight_kg,
        "streak": _streak(logged_dates, day),
    }

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Food, MealLog, WaterLog, WeightLog, WorkoutLog, User
from app.schemas import MealLogIn, WaterLogIn, WeightLogIn, WorkoutLogIn
from app.serializers import meal_log_out, weight_out

router = APIRouter(prefix="/api", tags=["logs"])


# --- workouts --------------------------------------------------------------


@router.post("/logs/workout")
def log_workout(
    payload: WorkoutLogIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """One workout record per day — logged again, it updates in place."""
    log = (
        db.query(WorkoutLog)
        .filter(WorkoutLog.user_id == user.id, WorkoutLog.date == payload.date)
        .first()
    )
    if log is None:
        log = WorkoutLog(user_id=user.id, date=payload.date)
        db.add(log)
    log.day_index = payload.day_index
    log.title = payload.title
    log.duration_min = payload.duration_min
    log.rating = payload.rating
    log.notes = payload.notes
    log.completed = True
    db.commit()
    db.refresh(log)
    return {
        "id": log.id,
        "date": log.date,
        "day_index": log.day_index,
        "title": log.title,
        "duration_min": log.duration_min,
        "rating": log.rating,
        "notes": log.notes,
        "completed": log.completed,
    }


@router.get("/logs/workout")
def list_workouts(
    days: int = 60, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    logs = (
        db.query(WorkoutLog)
        .filter(WorkoutLog.user_id == user.id)
        .order_by(WorkoutLog.date.desc())
        .limit(max(1, min(days, 400)))
        .all()
    )
    return {
        "items": [
            {
                "id": log.id,
                "date": log.date,
                "day_index": log.day_index,
                "title": log.title,
                "duration_min": log.duration_min,
                "rating": log.rating,
                "notes": log.notes,
                "completed": log.completed,
            }
            for log in logs
        ]
    }


@router.delete("/logs/workout/{date}", status_code=204)
def delete_workout(
    date: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    db.query(WorkoutLog).filter(
        WorkoutLog.user_id == user.id, WorkoutLog.date == date
    ).delete(synchronize_session=False)
    db.commit()
    return None


# --- meals -----------------------------------------------------------------


@router.post("/logs/meal", status_code=201)
def log_meal(
    payload: MealLogIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    food = db.get(Food, payload.food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    log = MealLog(
        user_id=user.id,
        date=payload.date,
        slot=payload.slot,
        food_id=food.id,
        servings=payload.servings,
        kcal=round(food.kcal * payload.servings, 1),
        protein_g=round(food.protein_g * payload.servings, 1),
        carbs_g=round(food.carbs_g * payload.servings, 1),
        fat_g=round(food.fat_g * payload.servings, 1),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return meal_log_out(log)


@router.get("/logs/meal")
def list_meals(
    date: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(MealLog).filter(MealLog.user_id == user.id)
    if date:
        query = query.filter(MealLog.date == date)
    logs = query.order_by(MealLog.logged_at).all()
    return {"items": [meal_log_out(log) for log in logs]}


@router.delete("/logs/meal/{log_id}", status_code=204)
def delete_meal(
    log_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    log = db.get(MealLog, log_id)
    if log is None or log.user_id != user.id:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(log)
    db.commit()
    return None


# --- weight ----------------------------------------------------------------


@router.post("/logs/weight")
def log_weight(
    payload: WeightLogIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = (
        db.query(WeightLog)
        .filter(WeightLog.user_id == user.id, WeightLog.date == payload.date)
        .first()
    )
    if log is None:
        log = WeightLog(user_id=user.id, date=payload.date, weight_kg=payload.weight_kg)
        db.add(log)
    log.weight_kg = payload.weight_kg
    log.note = payload.note
    db.commit()
    db.refresh(log)
    return weight_out(log)


@router.get("/logs/weight")
def list_weight(
    days: int = 180, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    logs = (
        db.query(WeightLog)
        .filter(WeightLog.user_id == user.id)
        .order_by(WeightLog.date)
        .limit(max(1, min(days, 1000)))
        .all()
    )
    return {"items": [weight_out(log) for log in logs]}


# --- water -----------------------------------------------------------------


@router.post("/logs/water")
def log_water(
    payload: WaterLogIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    log = (
        db.query(WaterLog)
        .filter(WaterLog.user_id == user.id, WaterLog.date == payload.date)
        .first()
    )
    if log is None:
        log = WaterLog(user_id=user.id, date=payload.date, ml=0.0)
        db.add(log)
    log.ml = max(0.0, round(log.ml + payload.ml, 1))
    db.commit()
    return {"date": log.date, "ml": log.ml}


@router.get("/logs/water")
def get_water(
    date: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    log = (
        db.query(WaterLog)
        .filter(WaterLog.user_id == user.id, WaterLog.date == date)
        .first()
    )
    return {"date": date, "ml": log.ml if log else 0.0}


@router.get("/logs/summary")
def summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Small roll-up used on the Progress screen."""
    scope = {"user_id": user.id}
    return {
        "workouts_logged": db.query(WorkoutLog).filter_by(**scope).count(),
        "meals_logged": db.query(MealLog).filter_by(**scope).count(),
        "weights_logged": db.query(WeightLog).filter_by(**scope).count(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

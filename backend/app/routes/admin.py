from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db, get_or_create_profile, get_profile
from app.generate import apply_targets, regenerate_plan
from app.models import (
    Food,
    FoodPreference,
    MealLog,
    PlanMeal,
    PlanWorkout,
    User,
    WaterLog,
    WeightLog,
    WorkoutLog,
)
from app.schemas import RestoreIn
from app.serializers import food_out

router = APIRouter(prefix="/api/admin", tags=["admin"])

PROFILE_FIELDS = (
    "name",
    "sex",
    "age",
    "height_cm",
    "weight_kg",
    "goal",
    "activity_level",
    "level",
    "workouts_per_week",
    "equipment",
    "dietary_flags",
    "units",
)


def _clear_activity(db: Session, user_id: int) -> None:
    for model in (PlanMeal, PlanWorkout, MealLog, WorkoutLog, WeightLog, WaterLog):
        db.query(model).filter(model.user_id == user_id).delete(synchronize_session=False)
    db.commit()


@router.get("/backup")
def backup(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_profile(db, user)
    meal_logs = db.query(MealLog).filter(MealLog.user_id == user.id).all()
    return {
        "version": 2,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "account": user.username,
        "profile": {field: getattr(profile, field) for field in PROFILE_FIELDS}
        if profile
        else None,
        "menu": [
            {"food": row.food.name, "status": row.status}
            for row in db.query(FoodPreference).filter(FoodPreference.user_id == user.id).all()
            if row.food
        ],
        "custom_foods": [
            food_out(food)
            for food in db.query(Food)
            .filter(Food.is_custom.is_(True), Food.created_by == user.id)
            .all()
        ],
        "workout_logs": [
            {
                "date": log.date,
                "day_index": log.day_index,
                "title": log.title,
                "duration_min": log.duration_min,
                "rating": log.rating,
                "notes": log.notes,
            }
            for log in db.query(WorkoutLog).filter(WorkoutLog.user_id == user.id).all()
        ],
        "meal_logs": [
            {
                "date": log.date,
                "slot": log.slot,
                "food": log.food.name if log.food else None,
                "servings": log.servings,
                "kcal": log.kcal,
                "protein_g": log.protein_g,
                "carbs_g": log.carbs_g,
                "fat_g": log.fat_g,
            }
            for log in meal_logs
        ],
        "weight_logs": [
            {"date": log.date, "weight_kg": log.weight_kg, "note": log.note}
            for log in db.query(WeightLog).filter(WeightLog.user_id == user.id).all()
        ],
        "water_logs": [
            {"date": log.date, "ml": log.ml}
            for log in db.query(WaterLog).filter(WaterLog.user_id == user.id).all()
        ],
    }


@router.post("/restore")
def restore(
    payload: RestoreIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    profile = None
    if payload.profile:
        profile = get_or_create_profile(db, user)
        for field in PROFILE_FIELDS:
            if field in payload.profile:
                setattr(profile, field, payload.profile[field])
        apply_targets(profile)
        db.commit()

    _clear_activity(db, user.id)

    for row in payload.workout_logs:
        if not row.get("date"):
            continue
        db.add(
            WorkoutLog(
                user_id=user.id,
                date=row["date"],
                day_index=row.get("day_index", 0),
                title=row.get("title", ""),
                duration_min=row.get("duration_min", 0),
                rating=row.get("rating"),
                notes=row.get("notes"),
            )
        )

    for row in payload.weight_logs:
        if row.get("date"):
            db.add(
                WeightLog(user_id=user.id, date=row["date"], weight_kg=row["weight_kg"], note=row.get("note"))
            )

    for row in payload.water_logs:
        if row.get("date"):
            db.add(WaterLog(user_id=user.id, date=row["date"], ml=row.get("ml", 0.0)))

    for row in payload.meal_logs:
        if not row.get("date") or not row.get("food"):
            continue
        food = db.query(Food).filter(Food.name == row["food"]).first()
        if food is None:
            continue
        servings = row.get("servings", 1.0)
        db.add(
            MealLog(
                user_id=user.id,
                date=row["date"],
                slot=row.get("slot", "meal"),
                food_id=food.id,
                servings=servings,
                kcal=row.get("kcal", round(food.kcal * servings, 1)),
                protein_g=row.get("protein_g", round(food.protein_g * servings, 1)),
                carbs_g=row.get("carbs_g", round(food.carbs_g * servings, 1)),
                fat_g=row.get("fat_g", round(food.fat_g * servings, 1)),
            )
        )

    db.commit()
    if profile:
        regenerate_plan(db, user, profile)
    return {"ok": True, "restored": True}


@router.delete("/data")
def reset(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Start this account over: clears the profile, plan, logs and personal dishes.

    The account itself and the shared food library are left alone.
    """
    _clear_activity(db, user.id)
    db.query(FoodPreference).filter(FoodPreference.user_id == user.id).delete(
        synchronize_session=False
    )
    db.query(Food).filter(Food.is_custom.is_(True), Food.created_by == user.id).delete(
        synchronize_session=False
    )
    profile = get_profile(db, user)
    if profile:
        db.delete(profile)
    db.commit()
    return {"ok": True}

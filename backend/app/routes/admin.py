from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, get_or_create_profile, get_profile
from app.generate import apply_targets, regenerate_plan
from app.models import Food, MealLog, PlanMeal, PlanWorkout, WaterLog, WeightLog, WorkoutLog
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


def _clear_activity(db: Session) -> None:
    for model in (PlanMeal, PlanWorkout, MealLog, WorkoutLog, WeightLog, WaterLog):
        db.query(model).delete()
    db.commit()


@router.get("/backup")
def backup(db: Session = Depends(get_db)):
    profile = get_profile(db)
    return {
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "profile": {field: getattr(profile, field) for field in PROFILE_FIELDS}
        if profile
        else None,
        "custom_foods": [
            food_out(food) for food in db.query(Food).filter(Food.is_custom.is_(True)).all()
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
            for log in db.query(WorkoutLog).all()
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
            for log in db.query(MealLog).all()
        ],
        "weight_logs": [
            {"date": log.date, "weight_kg": log.weight_kg, "note": log.note}
            for log in db.query(WeightLog).all()
        ],
        "water_logs": [
            {"date": log.date, "ml": log.ml} for log in db.query(WaterLog).all()
        ],
    }


@router.post("/restore")
def restore(payload: RestoreIn, db: Session = Depends(get_db)):
    profile = None
    if payload.profile:
        profile = get_or_create_profile(db)
        for field in PROFILE_FIELDS:
            if field in payload.profile:
                setattr(profile, field, payload.profile[field])
        apply_targets(profile)
        db.commit()

    _clear_activity(db)

    for row in payload.workout_logs:
        if not row.get("date"):
            continue
        db.add(
            WorkoutLog(
                date=row["date"],
                day_index=row.get("day_index", 0),
                title=row.get("title", ""),
                duration_min=row.get("duration_min", 0),
                rating=row.get("rating"),
                notes=row.get("notes"),
            )
        )

    for row in payload.weight_logs:
        if not row.get("date"):
            continue
        db.add(
            WeightLog(
                date=row["date"],
                weight_kg=row["weight_kg"],
                note=row.get("note"),
            )
        )

    for row in payload.water_logs:
        if row.get("date"):
            db.add(WaterLog(date=row["date"], ml=row.get("ml", 0.0)))

    for row in payload.meal_logs:
        if not row.get("date") or not row.get("food"):
            continue
        food = db.query(Food).filter(Food.name == row["food"]).first()
        if food is None:
            continue
        servings = row.get("servings", 1.0)
        db.add(
            MealLog(
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
        regenerate_plan(db, profile)
    return {"ok": True, "restored": True}


@router.delete("/data")
def reset(db: Session = Depends(get_db)):
    """Start over — removes the profile, the plan, every log and any custom dishes."""
    _clear_activity(db)
    for food in db.query(Food).filter(Food.is_custom.is_(True)).all():
        db.delete(food)
    profile = get_profile(db)
    if profile:
        db.delete(profile)
    db.commit()
    return {"ok": True}

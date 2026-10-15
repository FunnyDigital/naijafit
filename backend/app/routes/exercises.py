from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Exercise
from app.serializers import exercise_out

router = APIRouter(prefix="/api", tags=["exercises"])


@router.get("/exercises")
def list_exercises(
    category: str | None = None,
    equipment: str | None = None,
    level: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Exercise)
    if category:
        query = query.filter(Exercise.category == category)
    if equipment:
        query = query.filter(Exercise.equipment == equipment)
    if level:
        query = query.filter(Exercise.level == level)
    if q:
        query = query.filter(Exercise.name.ilike(f"%{q}%"))

    exercises = query.order_by(Exercise.category, Exercise.name).all()
    categories = [row[0] for row in db.query(Exercise.category).distinct().all()]

    return {
        "items": [exercise_out(exercise) for exercise in exercises],
        "count": len(exercises),
        "categories": sorted(categories),
    }


@router.get("/exercises/{exercise_id}")
def read_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        return {"error": "Exercise not found"}
    return exercise_out(exercise)

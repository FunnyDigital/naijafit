import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Exercise, Food, Meta

DATA_DIR = Path(__file__).resolve().parent / "data"
CATALOG_VERSION = "1"


def _load(filename: str) -> list[dict]:
    with open(DATA_DIR / filename, encoding="utf-8") as handle:
        return json.load(handle)


def _seed_foods(db: Session) -> int:
    existing = {name for (name,) in db.query(Food.name).all()}
    added = 0
    for row in _load("foods.json"):
        if row["name"] in existing:
            continue
        db.add(Food(**row))
        added += 1
    return added


def _seed_exercises(db: Session) -> int:
    existing = {name for (name,) in db.query(Exercise.name).all()}
    added = 0
    for row in _load("exercises.json"):
        if row["name"] in existing:
            continue
        db.add(Exercise(**row))
        added += 1
    return added


def seed_database() -> None:
    """Create the tables and fill the food/exercise catalogs. Safe to run repeatedly."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        foods = _seed_foods(db)
        exercises = _seed_exercises(db)

        marker = db.get(Meta, "catalog_version")
        if marker is None:
            db.add(Meta(key="catalog_version", value=CATALOG_VERSION))
        else:
            marker.value = CATALOG_VERSION

        db.commit()
        if foods or exercises:
            print(f"[seed] Added {foods} foods and {exercises} exercises")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

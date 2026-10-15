from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Food, MealLog, PlanMeal
from app.schemas import FoodIn
from app.serializers import food_out

router = APIRouter(prefix="/api", tags=["foods"])


@router.get("/foods")
def list_foods(
    category: str | None = None,
    tag: str | None = None,
    slot: str | None = None,
    q: str | None = None,
    limit: int = 300,
    db: Session = Depends(get_db),
):
    query = db.query(Food)
    if category:
        query = query.filter(Food.category == category)
    if q:
        query = query.filter(Food.name.ilike(f"%{q}%"))

    foods = query.order_by(Food.category, Food.name).all()
    if tag:
        foods = [food for food in foods if tag in (food.tags or [])]
    if slot:
        foods = [food for food in foods if slot in (food.meal_slots or [])]

    categories = sorted({row[0] for row in db.query(Food.category).distinct().all()})
    tags = sorted({value for food in db.query(Food).all() for value in (food.tags or [])})

    return {
        "items": [food_out(food) for food in foods[: max(1, limit)]],
        "count": len(foods),
        "categories": categories,
        "tags": tags,
    }


@router.get("/foods/{food_id}")
def read_food(food_id: int, db: Session = Depends(get_db)):
    food = db.get(Food, food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    return food_out(food)


@router.post("/foods", status_code=201)
def create_food(payload: FoodIn, db: Session = Depends(get_db)):
    food = Food(**payload.model_dump(), is_custom=True)
    db.add(food)
    db.commit()
    db.refresh(food)
    return food_out(food)


@router.put("/foods/{food_id}")
def update_food(food_id: int, payload: FoodIn, db: Session = Depends(get_db)):
    food = db.get(Food, food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    for field, value in payload.model_dump().items():
        setattr(food, field, value)
    db.commit()
    db.refresh(food)
    return food_out(food)


@router.delete("/foods/{food_id}", status_code=204)
def delete_food(food_id: int, db: Session = Depends(get_db)):
    food = db.get(Food, food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    if not food.is_custom:
        raise HTTPException(status_code=400, detail="Only dishes you added can be deleted")

    db.query(PlanMeal).filter(
        (PlanMeal.food_id == food_id) | (PlanMeal.paired_food_id == food_id)
    ).delete(synchronize_session=False)
    db.query(MealLog).filter(MealLog.food_id == food_id).delete(synchronize_session=False)
    db.delete(food)
    db.commit()
    return None

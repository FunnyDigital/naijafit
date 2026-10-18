import random
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db, get_profile
from app.generate import liked_food_ids
from app.mealplanner import is_allowed
from app.models import Food, FoodPreference, MealLog, PlanMeal, User
from app.schemas import FoodIn, MenuIn
from app.serializers import food_out

router = APIRouter(prefix="/api", tags=["foods"])

CATEGORY_BLURB = {
    "breakfast": "you have no breakfasts yet",
    "swallow": "you have no swallows yet",
    "soup": "you have no soups yet",
    "stew": "you have no stews yet",
    "rice": "you have no rice dishes yet",
    "porridge": "you have no beans or porridge yet",
    "protein": "you have no proteins yet",
    "side": "you have no sides yet",
    "snack": "you have no snacks yet",
    "fruit": "you have no fruit yet",
    "drink": "you have no drinks yet",
}


# --- catalog ---------------------------------------------------------------


@router.get("/foods")
def list_foods(
    category: str | None = None,
    tag: str | None = None,
    slot: str | None = None,
    q: str | None = None,
    limit: int = 300,
    user: User = Depends(get_current_user),
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
def read_food(food_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    food = db.get(Food, food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    return food_out(food)


@router.post("/foods", status_code=201)
def create_food(
    payload: FoodIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    food = Food(**payload.model_dump(), is_custom=True, created_by=user.id)
    db.add(food)
    db.commit()
    db.refresh(food)
    return food_out(food)


def _own_custom_food(db: Session, food_id: int, user: User) -> Food:
    food = db.get(Food, food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    if not food.is_custom:
        raise HTTPException(status_code=400, detail="That dish is part of the shared library")
    if food.created_by is not None and food.created_by != user.id:
        raise HTTPException(status_code=403, detail="That dish belongs to someone else")
    return food


@router.put("/foods/{food_id}")
def update_food(
    food_id: int,
    payload: FoodIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    food = _own_custom_food(db, food_id, user)
    for field, value in payload.model_dump().items():
        setattr(food, field, value)
    db.commit()
    db.refresh(food)
    return food_out(food)


@router.delete("/foods/{food_id}", status_code=204)
def delete_food(
    food_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    food = _own_custom_food(db, food_id, user)

    db.query(PlanMeal).filter(
        PlanMeal.user_id == user.id,
        (PlanMeal.food_id == food_id) | (PlanMeal.paired_food_id == food_id),
    ).delete(synchronize_session=False)
    db.query(MealLog).filter(
        MealLog.user_id == user.id, MealLog.food_id == food_id
    ).delete(synchronize_session=False)
    db.query(FoodPreference).filter(
        FoodPreference.food_id == food_id
    ).delete(synchronize_session=False)
    db.delete(food)
    db.commit()
    return None


# --- personal menu ---------------------------------------------------------


@router.get("/menu")
def read_menu(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(FoodPreference).filter(FoodPreference.user_id == user.id).all()
    liked = [row.food_id for row in rows if row.status == "liked"]
    disliked = [row.food_id for row in rows if row.status == "disliked"]
    total = db.query(Food).count()
    return {
        "liked_ids": liked,
        "disliked_ids": disliked,
        "liked_count": len(liked),
        "catalog_size": total,
        "using_menu": bool(liked),
    }


@router.post("/menu/{food_id}")
def set_menu_item(
    food_id: int,
    payload: MenuIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    food = db.get(Food, food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Dish not found")

    row = (
        db.query(FoodPreference)
        .filter(FoodPreference.user_id == user.id, FoodPreference.food_id == food_id)
        .first()
    )
    if row is None:
        row = FoodPreference(user_id=user.id, food_id=food_id, status=payload.status)
        db.add(row)
    else:
        row.status = payload.status
    db.commit()

    liked = liked_food_ids(db, user.id)
    return {"liked_ids": sorted(liked), "liked_count": len(liked), "using_menu": bool(liked)}


@router.delete("/menu/{food_id}")
def clear_menu_item(
    food_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    db.query(FoodPreference).filter(
        FoodPreference.user_id == user.id, FoodPreference.food_id == food_id
    ).delete(synchronize_session=False)
    db.commit()

    liked = liked_food_ids(db, user.id)
    return {"liked_ids": sorted(liked), "liked_count": len(liked), "using_menu": bool(liked)}


@router.get("/menu/suggestions")
def suggestions(
    limit: int = 6,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dishes worth adding: first what they're missing, then a bit of variety."""
    profile = get_profile(db, user)
    flags = set(profile.dietary_flags or []) if profile else set()

    rows = db.query(FoodPreference).filter(FoodPreference.user_id == user.id).all()
    liked = {row.food_id for row in rows if row.status == "liked"}
    disliked = {row.food_id for row in rows if row.status == "disliked"}

    foods = [food for food in db.query(Food).all() if is_allowed(food, flags)]
    by_id = {food.id: food for food in foods}
    counts = Counter(by_id[food_id].category for food_id in liked if food_id in by_id)

    pool = [food for food in foods if food.id not in liked and food.id not in disliked]
    rng = random.Random(user.id * 7919 + len(liked))
    rng.shuffle(pool)
    # Categories they have nothing for float to the top; then protein-dense picks.
    pool.sort(
        key=lambda food: (
            counts.get(food.category, 0),
            0 if "high_protein" in (food.tags or []) else 1,
        )
    )

    picks: list[dict] = []
    per_category: Counter = Counter()
    for food in pool:
        if len(picks) >= max(1, min(limit, 20)):
            break
        if per_category[food.category] >= 2:
            continue
        per_category[food.category] += 1

        if counts.get(food.category, 0) == 0:
            reason = CATEGORY_BLURB.get(food.category, "something new")
        elif "high_protein" in (food.tags or []):
            reason = "adds protein"
        elif food.kcal and food.kcal <= 130:
            reason = "a lighter option"
        else:
            reason = "adds variety"

        picks.append({**food_out(food), "reason": reason})

    return {"items": picks, "count": len(picks), "missing_categories": sorted(set(CATEGORY_BLURB) - set(counts))}

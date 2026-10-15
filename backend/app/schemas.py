from typing import Literal, Optional

from pydantic import BaseModel, Field

Goal = Literal["lose", "maintain", "gain"]
Sex = Literal["male", "female"]
ActivityLevel = Literal["sedentary", "light", "moderate", "active", "very_active"]
TrainingLevel = Literal["beginner", "intermediate", "advanced"]
Equipment = Literal["none", "chair", "band", "dumbbell"]
DietFlag = Literal["vegetarian", "gluten_free", "lactose_free"]
MealSlot = Literal["breakfast", "lunch", "dinner", "snack", "extra"]


class ProfileIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sex: Sex = "male"
    age: int = Field(default=30, ge=12, le=100)
    height_cm: float = Field(default=170, gt=90, lt=260)
    weight_kg: float = Field(default=75, gt=25, lt=350)
    goal: Goal = "lose"
    activity_level: ActivityLevel = "light"
    level: TrainingLevel = "beginner"
    workouts_per_week: int = Field(default=3, ge=1, le=7)
    equipment: list[Equipment] = Field(default_factory=list)
    dietary_flags: list[DietFlag] = Field(default_factory=list)
    units: Literal["metric", "imperial"] = "metric"


class FoodIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    name_local: Optional[str] = Field(default=None, max_length=160)
    category: str = Field(default="snack", max_length=40)
    meal_slots: list[MealSlot] = Field(default_factory=list)
    serving_desc: str = Field(default="1 serving", max_length=80)
    serving_grams: float = Field(default=100, ge=0, le=5000)
    kcal: float = Field(default=0, ge=0, le=5000)
    protein_g: float = Field(default=0, ge=0, le=500)
    carbs_g: float = Field(default=0, ge=0, le=1000)
    fat_g: float = Field(default=0, ge=0, le=500)
    fiber_g: float = Field(default=0, ge=0, le=200)
    sodium_mg: float = Field(default=0, ge=0, le=20000)
    tags: list[str] = Field(default_factory=list)
    photo_url: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = None


class WorkoutLogIn(BaseModel):
    date: str = Field(min_length=10, max_length=10)
    day_index: int = Field(default=0, ge=0, le=6)
    title: str = Field(default="", max_length=120)
    duration_min: int = Field(default=0, ge=0, le=600)
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    notes: Optional[str] = None


class MealLogIn(BaseModel):
    date: str = Field(min_length=10, max_length=10)
    slot: str = Field(default="meal", max_length=16)
    food_id: int
    servings: float = Field(default=1.0, gt=0, le=20)


class WeightLogIn(BaseModel):
    date: str = Field(min_length=10, max_length=10)
    weight_kg: float = Field(gt=25, lt=350)
    note: Optional[str] = Field(default=None, max_length=200)


class WaterLogIn(BaseModel):
    date: str = Field(min_length=10, max_length=10)
    ml: float = Field(gt=-2000, le=5000)


class RestoreIn(BaseModel):
    profile: Optional[dict] = None
    workout_logs: list[dict] = Field(default_factory=list)
    meal_logs: list[dict] = Field(default_factory=list)
    weight_logs: list[dict] = Field(default_factory=list)
    water_logs: list[dict] = Field(default_factory=list)

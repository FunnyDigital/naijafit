from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Profile(Base):
    """The one person using the app. A single row, always id=1."""

    __tablename__ = "profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    name: Mapped[str] = mapped_column(String(120), default="Friend")
    sex: Mapped[str] = mapped_column(String(16), default="male")
    age: Mapped[int] = mapped_column(Integer, default=30)
    height_cm: Mapped[float] = mapped_column(Float, default=170.0)
    weight_kg: Mapped[float] = mapped_column(Float, default=75.0)
    goal: Mapped[str] = mapped_column(String(16), default="lose")
    activity_level: Mapped[str] = mapped_column(String(24), default="light")
    level: Mapped[str] = mapped_column(String(16), default="beginner")
    workouts_per_week: Mapped[int] = mapped_column(Integer, default=3)
    equipment: Mapped[list] = mapped_column(JSON, default=list)
    dietary_flags: Mapped[list] = mapped_column(JSON, default=list)
    units: Mapped[str] = mapped_column(String(16), default="metric")

    bmr: Mapped[float] = mapped_column(Float, default=0.0)
    tdee: Mapped[float] = mapped_column(Float, default=0.0)
    calorie_target: Mapped[float] = mapped_column(Float, default=0.0)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, default=0.0)
    water_ml: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)


class Food(Base):
    """A Nigerian dish or food item. Seeded, and extendable by the user."""

    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    name_local: Mapped[str | None] = mapped_column(String(160), nullable=True)
    category: Mapped[str] = mapped_column(String(40), index=True)
    meal_slots: Mapped[list] = mapped_column(JSON, default=list)
    serving_desc: Mapped[str] = mapped_column(String(80), default="1 serving")
    serving_grams: Mapped[float] = mapped_column(Float, default=100.0)
    kcal: Mapped[float] = mapped_column(Float, default=0.0)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, default=0.0)
    fiber_g: Mapped[float] = mapped_column(Float, default=0.0)
    sodium_mg: Mapped[float] = mapped_column(Float, default=0.0)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)


class Exercise(Base):
    """A home exercise. Equipment is one of none/band/dumbbell/chair."""

    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    category: Mapped[str] = mapped_column(String(24), index=True)
    primary_muscles: Mapped[list] = mapped_column(JSON, default=list)
    equipment: Mapped[str] = mapped_column(String(24), default="none")
    level: Mapped[str] = mapped_column(String(16), default="beginner")
    instructions: Mapped[str] = mapped_column(Text, default="")
    is_timed: Mapped[bool] = mapped_column(Boolean, default=False)
    default_sets: Mapped[int] = mapped_column(Integer, default=3)
    default_reps: Mapped[int] = mapped_column(Integer, default=12)
    default_seconds: Mapped[int] = mapped_column(Integer, default=40)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)


class PlanWorkout(Base):
    __tablename__ = "plan_workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day_index: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(120), default="Workout")
    focus: Mapped[str] = mapped_column(String(60), default="")
    est_minutes: Mapped[int] = mapped_column(Integer, default=30)
    is_rest_day: Mapped[bool] = mapped_column(Boolean, default=False)

    items: Mapped[list["PlanWorkoutItem"]] = relationship(
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="PlanWorkoutItem.order_index",
    )


class PlanWorkoutItem(Base):
    __tablename__ = "plan_workout_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_id: Mapped[int] = mapped_column(
        ForeignKey("plan_workouts.id", ondelete="CASCADE")
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    section: Mapped[str] = mapped_column(String(16), default="main")
    sets: Mapped[int] = mapped_column(Integer, default=3)
    reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rest_sec: Mapped[int] = mapped_column(Integer, default=45)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)

    workout: Mapped["PlanWorkout"] = relationship(back_populates="items")
    exercise: Mapped["Exercise"] = relationship()


class PlanMeal(Base):
    __tablename__ = "plan_meals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day_index: Mapped[int] = mapped_column(Integer, index=True)
    slot: Mapped[str] = mapped_column(String(16), index=True)
    food_id: Mapped[int] = mapped_column(ForeignKey("foods.id"))
    paired_food_id: Mapped[int | None] = mapped_column(
        ForeignKey("foods.id"), nullable=True
    )
    servings: Mapped[float] = mapped_column(Float, default=1.0)
    paired_servings: Mapped[float] = mapped_column(Float, default=0.0)
    kcal: Mapped[float] = mapped_column(Float, default=0.0)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, default=0.0)

    food: Mapped["Food"] = relationship(foreign_keys=[food_id])
    paired_food: Mapped["Food | None"] = relationship(foreign_keys=[paired_food_id])


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(String(10), index=True)
    day_index: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(120), default="")
    duration_min: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class MealLog(Base):
    __tablename__ = "meal_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(String(10), index=True)
    slot: Mapped[str] = mapped_column(String(16), default="meal")
    food_id: Mapped[int] = mapped_column(ForeignKey("foods.id"))
    servings: Mapped[float] = mapped_column(Float, default=1.0)
    kcal: Mapped[float] = mapped_column(Float, default=0.0)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, default=0.0)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    food: Mapped["Food"] = relationship()


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    weight_kg: Mapped[float] = mapped_column(Float)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)


class WaterLog(Base):
    __tablename__ = "water_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(String(10), index=True)
    ml: Mapped[float] = mapped_column(Float, default=0.0)


class Meta(Base):
    __tablename__ = "meta"

    key: Mapped[str] = mapped_column(String(60), primary_key=True)
    value: Mapped[str] = mapped_column(String(200), default="")

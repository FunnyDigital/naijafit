from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["meta"])

OPTIONS = {
    "goals": [
        {"value": "lose", "label": "Lose fat", "hint": "A gentle calorie deficit, higher protein."},
        {"value": "maintain", "label": "Stay the same", "hint": "Eat around your maintenance calories."},
        {"value": "gain", "label": "Build muscle", "hint": "A small surplus with heavier training."},
    ],
    "sexes": [
        {"value": "male", "label": "Male"},
        {"value": "female", "label": "Female"},
    ],
    "activity_levels": [
        {"value": "sedentary", "label": "Sedentary", "hint": "Desk job, little walking."},
        {"value": "light", "label": "Lightly active", "hint": "Some walking or chores most days."},
        {"value": "moderate", "label": "Moderately active", "hint": "On your feet a lot, or sport 3–5 days."},
        {"value": "active", "label": "Very active", "hint": "Hard training most days."},
        {"value": "very_active", "label": "Extremely active", "hint": "Physical job plus training."},
    ],
    "levels": [
        {"value": "beginner", "label": "Beginner", "hint": "New to exercise, or back after a break."},
        {"value": "intermediate", "label": "Intermediate", "hint": "Training on and off for a while."},
        {"value": "advanced", "label": "Advanced", "hint": "Consistent, and comfortable with harder moves."},
    ],
    "equipment": [
        {"value": "none", "label": "Just my bodyweight", "hint": "No equipment at all."},
        {"value": "chair", "label": "A chair or step", "hint": "For dips, step-ups and split squats."},
        {"value": "band", "label": "Resistance band", "hint": "For rows, presses and pull-aparts."},
        {"value": "dumbbell", "label": "Dumbbells", "hint": "For presses, rows and squats."},
    ],
    "dietary_flags": [
        {"value": "vegetarian", "label": "Vegetarian", "hint": "Only plant-based dishes are planned."},
        {"value": "gluten_free", "label": "Gluten free", "hint": "Swallows and bakes with gluten are skipped."},
        {"value": "lactose_free", "label": "Lactose free", "hint": "Milky drinks are skipped."},
    ],
    "workout_days": [2, 3, 4, 5, 6],
    "food_categories": [
        "breakfast",
        "swallow",
        "soup",
        "stew",
        "rice",
        "porridge",
        "protein",
        "side",
        "snack",
        "fruit",
        "drink",
    ],
    "food_tags": ["high_protein", "low_carb", "low_fat", "vegan", "high_fiber", "gluten_free", "light"],
    "exercise_categories": ["push", "pull", "legs", "core", "cardio", "mobility", "full_body"],
}


@router.get("/onboarding/options")
def onboarding_options():
    return OPTIONS

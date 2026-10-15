from app.models import Exercise, Food, MealLog, PlanMeal, PlanWorkout, Profile, WeightLog


def food_out(food: Food | None) -> dict | None:
    if food is None:
        return None
    return {
        "id": food.id,
        "name": food.name,
        "name_local": food.name_local,
        "category": food.category,
        "meal_slots": food.meal_slots or [],
        "serving_desc": food.serving_desc,
        "serving_grams": food.serving_grams,
        "kcal": food.kcal,
        "protein_g": food.protein_g,
        "carbs_g": food.carbs_g,
        "fat_g": food.fat_g,
        "fiber_g": food.fiber_g,
        "sodium_mg": food.sodium_mg,
        "tags": food.tags or [],
        "photo_url": food.photo_url,
        "notes": food.notes,
        "is_custom": food.is_custom,
    }


def exercise_out(exercise: Exercise) -> dict:
    return {
        "id": exercise.id,
        "name": exercise.name,
        "category": exercise.category,
        "primary_muscles": exercise.primary_muscles or [],
        "equipment": exercise.equipment,
        "level": exercise.level,
        "instructions": exercise.instructions,
        "is_timed": exercise.is_timed,
        "default_sets": exercise.default_sets,
        "default_reps": exercise.default_reps,
        "default_seconds": exercise.default_seconds,
        "photo_url": exercise.photo_url,
        "video_url": exercise.video_url,
    }


def workout_item_out(item) -> dict:
    return {
        "id": item.id,
        "order_index": item.order_index,
        "section": item.section,
        "sets": item.sets,
        "reps": item.reps,
        "seconds": item.seconds,
        "rest_sec": item.rest_sec,
        "note": item.note,
        "exercise": exercise_out(item.exercise),
    }


def workout_out(workout: PlanWorkout) -> dict:
    items = [workout_item_out(item) for item in workout.items]
    return {
        "id": workout.id,
        "day_index": workout.day_index,
        "title": workout.title,
        "focus": workout.focus,
        "est_minutes": workout.est_minutes,
        "is_rest_day": workout.is_rest_day,
        "total_exercises": len(items),
        "items": items,
    }


def plan_workout_placeholder(day_index: int) -> dict:
    return {
        "id": None,
        "day_index": day_index,
        "title": "No plan yet",
        "focus": "Finish onboarding to get your plan",
        "est_minutes": 0,
        "is_rest_day": True,
        "total_exercises": 0,
        "items": [],
    }


def meal_out(meal: PlanMeal) -> dict:
    return {
        "id": meal.id,
        "day_index": meal.day_index,
        "slot": meal.slot,
        "servings": meal.servings,
        "paired_servings": meal.paired_servings,
        "kcal": meal.kcal,
        "protein_g": meal.protein_g,
        "carbs_g": meal.carbs_g,
        "fat_g": meal.fat_g,
        "food": food_out(meal.food),
        "paired_food": food_out(meal.paired_food),
    }


def meal_log_out(log: MealLog) -> dict:
    return {
        "id": log.id,
        "date": log.date,
        "slot": log.slot,
        "food_id": log.food_id,
        "servings": log.servings,
        "kcal": log.kcal,
        "protein_g": log.protein_g,
        "carbs_g": log.carbs_g,
        "fat_g": log.fat_g,
        "food": food_out(log.food),
    }


def weight_out(log: WeightLog) -> dict:
    return {"id": log.id, "date": log.date, "weight_kg": log.weight_kg, "note": log.note}


def targets_out(profile: Profile) -> dict:
    return {
        "bmr": profile.bmr,
        "tdee": profile.tdee,
        "calorie_target": profile.calorie_target,
        "protein_g": profile.protein_g,
        "carbs_g": profile.carbs_g,
        "fat_g": profile.fat_g,
        "water_ml": profile.water_ml,
    }


def profile_out(profile: Profile) -> dict:
    return {
        "id": profile.id,
        "name": profile.name,
        "sex": profile.sex,
        "age": profile.age,
        "height_cm": profile.height_cm,
        "weight_kg": profile.weight_kg,
        "goal": profile.goal,
        "activity_level": profile.activity_level,
        "level": profile.level,
        "workouts_per_week": profile.workouts_per_week,
        "equipment": profile.equipment or [],
        "dietary_flags": profile.dietary_flags or [],
        "units": profile.units,
        "targets": targets_out(profile),
    }

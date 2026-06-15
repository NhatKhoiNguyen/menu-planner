from bson import ObjectId
from flask import current_app
from app.models.meal import serialize_meal

def suggest_similar_meals(meal_id):
    db = current_app.db
    meals_collection = db.meals

    target_meal = meals_collection.find_one({"_id": ObjectId(meal_id)})
    if not target_meal:
        return []

    all_meals = list(meals_collection.find({"_id": {"$ne": ObjectId(meal_id)}}))
    target_tags = set(target_meal.get("tags", []))

    def similarity(m):
        tags = set(m.get("tags", []))
        return len(tags & target_tags)

    sorted_meals = sorted(all_meals, key=similarity, reverse=True)
    return [serialize_meal(m) for m in sorted_meals[:6]]

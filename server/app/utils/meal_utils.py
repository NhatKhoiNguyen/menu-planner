def meal_to_dict(meal, original_calories=None, original_cost=None):
    result = {
        "id": str(meal["_id"]) if "_id" in meal else None,
        "name": meal["title"],
        "calories": meal["energy"],
        "price": meal["price"],
        "tags": meal["tags"],
        "ingredients": meal.get("ingredients", []),
        "image": meal.get("main_image", ""),
        "steps": meal.get("steps", [])
    }
    if original_calories is not None:
        result["original_calories"] = original_calories
    if original_cost is not None:
        result["original_cost"] = original_cost
    return result
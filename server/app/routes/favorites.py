from flask import Blueprint, request, jsonify, current_app
from app.utils.auth_decorator import login_required
from bson import ObjectId
favorites_bp = Blueprint("favorites", __name__, url_prefix="/api/favorites")

# @favorites_bp.route("/add", methods=["POST"])
# @login_required
# def add_favorite(current_user):
#     user_id = str(current_user["_id"])
#     meal = request.json.get("meal")

#     if not meal:
#         return jsonify({"error": "Missing meal"}), 400

#     current_app.db.favorites.update_one(
#         {"user_id": user_id},
#         {"$addToSet": {"meal_ids": meal_id}},
#         upsert=True
#     )
#     return jsonify({"message": "Meal added to favorites"})

# @favorites_bp.route("/list", methods=["GET"])
# @login_required
# def get_favorites(current_user):
#     user_id = str(current_user["_id"])
#     favs = current_app.db.favorites.find_one({"user_id": user_id})
#     return jsonify({"meals": favs["meals"] if favs else []})

# @favorites_bp.route("/remove/<meal_id>", methods=["DELETE"])
# @login_required
# def remove_favorite(current_user, meal_id):
#     user_id = str(current_user["_id"])

#     result = current_app.db.favorites.update_one(
#         {"user_id": user_id},
#         {"$pull": {"meals": {"id": meal_id}}}
#     )

#     if result.modified_count == 0:
#         return jsonify({"error": "Món không tồn tại trong danh sách yêu thích"}), 404

#     return jsonify({"message": "Đã xóa khỏi danh sách yêu thích"}), 200

@favorites_bp.route("/add", methods=["POST"])
@login_required
def add_favorite(current_user):
    user_id = current_user["_id"]
    meal_id = request.json.get("meal_id")

    if not meal_id:
        return jsonify({"error": "Missing meal_id"}), 400

    # Ensure meal exists
    try:
        meal_obj_id = ObjectId(meal_id)
    except Exception:
        return jsonify({"error": "Invalid meal_id format"}), 400

    meal = current_app.db.meals.find_one({"_id": meal_obj_id})
    if not meal:
        return jsonify({"error": "Meal not found"}), 404

    current_app.db.favorites.update_one(
        {"user_id": user_id},
        {"$addToSet": {"meal_ids": ObjectId(meal_id)}},
        upsert=True
    )

    return jsonify({"message": "Meal added to favorites"}), 200


@favorites_bp.route("/list", methods=["GET"])
@login_required
def get_favorites(current_user):
    user_id = current_user["_id"]

    favs = current_app.db.favorites.find_one({"user_id": user_id})
    if not favs or "meal_ids" not in favs:
        return jsonify({"meals": []})

    meals = list(current_app.db.meals.find({"_id": {"$in": favs["meal_ids"]}}))

    for meal in meals:
        meal["_id"] = str(meal["_id"])

    return jsonify({"meals": meals}), 200


@favorites_bp.route("/remove/<meal_id>", methods=["DELETE"])
@login_required
def remove_favorite(current_user, meal_id):
    user_id = current_user["_id"]

    # Remove the string ID
    result = current_app.db.favorites.update_one(
        {"user_id": user_id},
        {"$pull": {"meal_ids": ObjectId(meal_id)}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "Meal not found in favorites"}), 404

    return jsonify({"message": "Meal removed from favorites"}), 200
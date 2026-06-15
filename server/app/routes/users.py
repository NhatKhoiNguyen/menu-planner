from flask import Blueprint, request, jsonify, current_app
from app.models.user import User
from datetime import datetime
from app.utils.auth_decorator import login_required
import json
from app.utils.password_utils import hash_password
from bson import ObjectId
from copy import deepcopy
import re

users_bp = Blueprint("users", __name__, url_prefix="/api/users")

def normalize_amount_str(amount_str, servings):
    if not isinstance(amount_str, str):
        return amount_str

    match = re.match(r"^\s*([\d.,]+)\s*(\D*)$", amount_str.strip())
    if not match:
        return amount_str 

    number_part, unit_part = match.groups()
    number_part = number_part.replace(",", ".")

    try:
        value = float(number_part)
        value_per_serving = round(value / servings, 2)
        if value_per_serving.is_integer():
            number_formatted = str(int(value_per_serving))
        else:
            number_formatted = f"{value_per_serving:.2f}".rstrip("0").rstrip(".")

        return f"{number_formatted} {unit_part.strip()}".strip()
    except ValueError:
        return amount_str

@users_bp.route("/contribute", methods=["POST"])
@login_required
def contribute_meal(current_user):
    data = request.json
    servings = max(data.get("servings", 1), 1)

    ingredients = deepcopy(data.get("ingredients", [])) 

    if servings > 1:
        for ing in ingredients:
            if "amount" in ing:
                ing["amount"] = normalize_amount_str(ing["amount"], servings)

    energy = data.get("energy", 0)
    if isinstance(energy, (int, float)):
        energy = int(round(energy / servings, 2))

    price = data.get("price", 0)
    if isinstance(price, (int, float)):
        price = int(round(price / servings, 2))

    new_meal = {
        "title": data["title"],
        "type": data["type"],
        "energy": energy,
        "tags": data.get("tags", []),
        "ingredients": ingredients,
        "steps": data.get("steps", []),
        "price": price,
        "servings": 1,
        "submittedBy": str(current_user["_id"]),
        "createdAt": datetime.utcnow(),
        "main_image": data.get("main_image"),
        "allergens": data.get("allergens", []),
    }
    current_app.db.pending_meals.insert_one(new_meal)
    return jsonify({"message": "Gửi món ăn thành công. Chờ duyệt."}), 201

@users_bp.route("/<user_id>", methods=["PUT"])
@login_required
def update_user(user_id, current_user):
    if str(current_user["_id"]) != user_id:
        return jsonify({"error": "Không có quyền chỉnh sửa người dùng này"}), 403

    data = request.json
    update_fields = {}

    if "username" in data and data["username"].strip():
        update_fields["username"] = data["username"].strip()

    if "password" in data and data["password"].strip():
        hashed_pw = hash_password(data["password"])
        update_fields["password"] = hashed_pw

    if not update_fields:
        updated_user = current_app.db.users.find_one({"_id": ObjectId(user_id)})
        return jsonify({
            "_id": str(updated_user["_id"]),
            "username": updated_user["username"],
            "email": updated_user["email"],
            "role": "admin" if updated_user.get("is_admin", False) else "user"
        }), 200


    try:
        user_before = current_app.db.users.find_one({"_id": ObjectId(user_id)})
        if user_before and "is_admin" not in update_fields:
            update_fields["is_admin"] = user_before.get("is_admin", False)
        current_app.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_fields}
        )

        updated_user = current_app.db.users.find_one({"_id": ObjectId(user_id)})

        return jsonify({
            "_id": str(updated_user["_id"]),
            "username": updated_user["username"],
            "email": updated_user["email"],
            "role": "admin" if updated_user.get("is_admin", False) else "user"
        }), 200

    except Exception as e:
        print("Error updating user:", e)
        return jsonify({"error": "Cập nhật thất bại"}), 500
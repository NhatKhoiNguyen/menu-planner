from flask import Blueprint, request, jsonify, current_app
from app.utils.auth_decorator import admin_required
from bson import ObjectId
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
import os
import json
import re
from copy import deepcopy
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

def generate_meal_embedding(meal):
    title = meal.get("title", "")
    tags = " ".join(meal.get("tags", []))
    ingredients = " ".join(i.get("name", "") for i in meal.get("ingredients", []))
    text = f"{title} {tags} {ingredients}"
    return model.encode(text).tolist()

@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_users(current_user):
    db = current_app.db
    search = request.args.get("search", "")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("pageSize", 10))

    query = {}
    if search:
        query["$or"] = [
            {"_id": {"$regex": search, "$options": "i"}},
            {"username": {"$regex": search, "$options": "i"}},
        ]

    users_cursor = db.users.find(query).skip((page - 1) * page_size).limit(page_size)
    total = db.users.count_documents(query)

    users = []
    for user in users_cursor:
        users.append({
            "_id": str(user["_id"]),
            "username": user.get("username", ""),
            "email": user.get("email", ""),
            "is_admin": user.get("is_admin", False),
        })

    return jsonify({
        "users": users,
        "total": total,
        "page": page,
        "pageSize": page_size
    })


@admin_bp.route("/users/<user_id>", methods=["PUT"])
@admin_required
def update_user(current_user, user_id):
    db = current_app.db
    data = request.json

    update_data = {}
    if "username" in data:
        update_data["username"] = data["username"]

    result = db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Không tìm thấy người dùng"}), 404

    updated_user = current_app.db.users.find_one({"_id": ObjectId(user_id)})
    updated_user["_id"] = str(updated_user["_id"])
    del updated_user["password"]

    return jsonify({
        "message": "Cập nhật thành công",
        "updated_user": updated_user
    })


@admin_bp.route("/users/<user_id>", methods=["DELETE"])
@admin_required
def delete_user(current_user, user_id):
    db = current_app.db
    result = db.users.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        return jsonify({"error": "Không tìm thấy người dùng"}), 404

    return jsonify({"message": "Đã xóa người dùng"})


@admin_bp.route("/meals", methods=["GET"])
@admin_required
def get_meals(current_user):
    db = current_app.db
    meals = list(db.meals.find({}))
    for meal in meals:
        meal["_id"] = str(meal["_id"])
    return jsonify({"meals": meals})



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

def normalize_ingredients(ingredients, servings):
    if servings <= 1:
        return ingredients
    normalized = []
    for ing in deepcopy(ingredients):
        if "amount" in ing:
            ing["amount"] = normalize_amount_str(ing["amount"], servings)
        normalized.append(ing)
    return normalized


@admin_bp.route("/meals", methods=["POST"])
@admin_required
def create_meal(current_user):
    db = current_app.db
    data = request.json

    required_fields = ["title", "energy", "price", "type", "servings", "tags", "ingredients", "allergens"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Thiếu trường bắt buộc: {field}"}), 400

    servings = max(data.get("servings", 1), 1)

    ingredients = normalize_ingredients(data.get("ingredients", []), servings)

    energy = int(round(data["energy"] / servings)) if isinstance(data["energy"], (int, float)) else 0
    price = int(round(data["price"] / servings)) if isinstance(data["price"], (int, float)) else 0

    meal = {
        "title": data["title"],
        "energy": energy,
        "price": price,
        "type": data["type"],
        "servings": 1,
        "tags": data.get("tags", []),
        "allergens": data.get("allergens", []),
        "ingredients": ingredients,
        "main_image": data.get("main_image", ""),
        "steps": data.get("steps", []),
    }

    meal["embedding"] = generate_meal_embedding(meal)

    result = db.meals.insert_one(meal)
    meal["_id"] = str(result.inserted_id)
    return jsonify({"message": "Đã thêm món ăn", "meal": meal})


@admin_bp.route("/meals/<meal_id>", methods=["PUT"])
@admin_required
def update_meal(current_user, meal_id):
    db = current_app.db
    data = request.json

    try:
        object_id = ObjectId(meal_id)
    except:
        return jsonify({"error": "ID không hợp lệ"}), 400
    
    servings = max(data.get("servings", 1), 1)
    ingredients = normalize_ingredients(data.get("ingredients", []), servings)

    update_fields = {
        "title": data.get("title"),
        "energy": int(round(data.get("energy", 0) / servings)) if data.get("energy") else None,
        "price": int(round(data.get("price", 0) / servings)) if data.get("price") else None,
        "type": data.get("type"),
        "main_image": data.get("main_image", ""),
        "ingredients": ingredients,
        "steps": data.get("steps", []),
        "tags": data.get("tags", []),
        "allergens": data.get("allergens", []),
        "servings": 1,
    }

    update_fields["embedding"] = generate_meal_embedding(update_fields)

    update_fields = {k: v for k, v in update_fields.items() if v is not None}

    result = db.meals.update_one({"_id": object_id}, {"$set": update_fields})

    if result.matched_count == 0:
        return jsonify({"error": "Không tìm thấy món ăn"}), 404

    updated = db.meals.find_one({"_id": object_id})
    updated["_id"] = str(updated["_id"])
    return jsonify({"message": "Đã cập nhật món ăn", "meal": updated})


@admin_bp.route("/meals/<meal_id>", methods=["DELETE"])
@admin_required
def delete_meal(current_user, meal_id):
    db = current_app.db
    result = db.meals.delete_one({"_id": ObjectId(meal_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Không tìm thấy món ăn"}), 404
    return jsonify({"message": "Đã xóa món ăn thành công"})




# load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")


# def gemini_call(prompt: str) -> str:
#     response = model.generate_content(prompt)
#     text = response.text.strip()
#     match = re.search(r'\[.*?\]', text, re.DOTALL)
#     if match:
#         return match.group(0)

#     return text

# @admin_bp.route("/auto/energy", methods=["POST"])
# @admin_required
# def auto_energy(current_user):
#     data = request.json
#     ingredients = data.get("ingredients", [])
#     if not ingredients or not isinstance(ingredients, list):
#         return jsonify({"error": "Thiếu hoặc sai định dạng nguyên liệu"}), 400

#     formatted = "\n".join(
#         f"- {i.get('name', '')}: {i.get('amount', '')}" for i in ingredients if i.get("name") and i.get("amount")
#     )

#     if not formatted.strip():
#         return jsonify({"error": "Chưa có nguyên liệu hợp lệ"}), 400

#     prompt = f"""Tính tổng lượng calories (kcal) cho món ăn từ danh sách nguyên liệu sau:
# {formatted}

# Chỉ trả lời một số duy nhất, không kèm đơn vị hoặc giải thích."""

#     try:
#         answer = gemini_call(prompt)
#         match = re.search(r"\d+(?:[\.,]\d+)?", answer)
#         if match:
#             value = match.group(0).replace(",", ".")
#             return jsonify({"energy": round(float(value), 2)})
#         else:
#             return jsonify({"error": "Không đọc được giá trị calo"}), 500
            
#     except Exception as e:
#         print("Gemini error:", str(e))
#         return jsonify({"error": "Không thể ước tính calories"}), 500


# @admin_bp.route("/auto/price", methods=["POST"])
# @admin_required
# def auto_price(current_user):
#     data = request.json
#     ingredients = data.get("ingredients", [])
#     if not ingredients or not isinstance(ingredients, list):
#         return jsonify({"error": "Thiếu hoặc sai định dạng nguyên liệu"}), 400

#     formatted = "\n".join(
#         f"- {i.get('name', '')}: {i.get('amount', '')}" for i in ingredients if i.get("name") and i.get("amount")
#     )

#     if not formatted.strip():
#         return jsonify({"error": "Chưa có nguyên liệu hợp lệ"}), 400

#     prompt = f"""Tính giá tiền ước lượng (đơn vị VNĐ) cho món ăn từ danh sách nguyên liệu sau:
# {formatted}

# Chỉ trả lời bằng một số duy nhất, không kèm đơn vị hoặc giải thích."""

#     try:
#         answer = gemini_call(prompt)
#         match = re.search(r"\d+(?:[\.,]\d+)?", answer)
#         if match:
#             value = match.group(0).replace(",", ".")
#             return jsonify({"price": round(float(value))})
#         else:
#             return jsonify({"error": "Không đọc được giá trị chi phí"}), 500
#     except Exception as e:
#         print("Gemini error:", str(e))
#         return jsonify({"error": "Không thể ước tính giá"}), 500


# @admin_bp.route("/auto/tags", methods=["POST"])
# @admin_required
# def auto_tags(current_user):
#     data = request.json
#     ingredients = data.get("ingredients", [])
#     ALLOWED_TAGS = [
#         "Món Á", "Món Âu", "Kết hợp Á - Âu", "Món chay",
#         "Ít dầu mỡ", "Không gluten", "Không lactose"
#     ]
#     if not ingredients or not isinstance(ingredients, list):
#         return jsonify({"error": "Thiếu hoặc sai định dạng nguyên liệu"}), 400

#     formatted = "\n".join(
#         f"- {i.get('name', '')}: {i.get('amount', '')}" for i in ingredients if i.get("name") and i.get("amount")
#     )

#     if not formatted.strip():
#         return jsonify({"error": "Chưa có nguyên liệu hợp lệ"}), 400

#     prompt = f"""Dựa vào danh sách nguyên liệu sau:
# {formatted}

# Chọn những tag phù hợp nhất từ danh sách bên dưới:
# {ALLOWED_TAGS}

# Chỉ trả lời bằng một mảng JSON duy nhất (không bọc trong ```), ví dụ: ["Món Á", "Không gluten"]"""

#     try:
#         answer = gemini_call(prompt)
#         print("Gemini raw answer (tags):", repr(answer))
#         if not answer.strip():
#             raise ValueError("Không có phản hồi từ Gemini")
#         cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", answer.strip(), flags=re.IGNORECASE)
#         tags = json.loads(cleaned)

#         if isinstance(tags, str):
#             tags = json.loads(tags)

#         if not isinstance(tags, list):
#             raise ValueError("Tags trả về không phải mảng")

#         filtered = [tag for tag in tags if tag in ALLOWED_TAGS]
#         return jsonify({"tags": filtered})
#     except Exception as e:
#         print("Gemini tag error:", str(e))
#         return jsonify({"error": "Không thể gợi ý thể loại món ăn"}), 500


# @admin_bp.route("/auto/allergens", methods=["POST"])
# @admin_required
# def auto_allergens(current_user):
#     data = request.get_json()
#     ingredients = data.get("ingredients", [])

#     ALLERGENS = ["Trứng", "Hải sản", "Sữa", "Đậu phộng", "Đậu nành", "Lúa mì"]

#     if not ingredients or not isinstance(ingredients, list):
#         return jsonify({"error": "Thiếu hoặc sai định dạng nguyên liệu"}), 400

#     formatted = "\n".join(
#         f"- {i.get('name', '')}: {i.get('amount', '')}" for i in ingredients if i.get("name") and i.get("amount")
#     )

#     if not formatted.strip():
#         return jsonify({"error": "Chưa có nguyên liệu hợp lệ"}), 400

#     prompt = f"""Dựa vào danh sách nguyên liệu sau:
# {formatted}

# Cho biết trong số các chất gây dị ứng sau có những chất nào:
# {ALLERGENS}

# Trả lời dưới dạng mảng JSON các chất gây dị ứng, ví dụ: ["Trứng", "Sữa"]"""

#     try:
#         answer = gemini_call(prompt)
#         print("Gemini raw answer (allergens):", repr(answer))

#         if not answer.strip():
#             raise ValueError("Không có phản hồi từ Gemini")

#         cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", answer.strip(), flags=re.IGNORECASE)

#         allergens = json.loads(cleaned)

#         # Nếu Gemini trả chuỗi JSON dạng string
#         if isinstance(allergens, str):
#             allergens = json.loads(allergens)

#         if not isinstance(allergens, list):
#             raise ValueError("Kết quả không hợp lệ")

#         filtered = [a for a in allergens if a in ALLERGENS]
#         return jsonify({"allergens": filtered})
#     except Exception as e:
#         print("Gemini allergen error:", str(e))
#         return jsonify({"error": "Không thể trích xuất dị ứng"}), 500


@admin_bp.route("/pending-meals", methods=["GET"])
@admin_required
def get_pending_meals(current_user):
    pending_meals = list(current_app.db.pending_meals.find())
    user_ids = list({meal["submittedBy"] for meal in pending_meals if "submittedBy" in meal})
    users = current_app.db.users.find({"_id": {"$in": [ObjectId(uid) for uid in user_ids]}})
    user_map = {str(user["_id"]): {"name": user["username"], "email": user["email"]} for user in users}
    for meal in pending_meals:
        uid = str(meal.get("submittedBy"))
        meal["contributorName"] = user_map.get(uid, {}).get("name", "Không rõ")
        meal["contributorEmail"] = user_map.get(uid, {}).get("email", "")
        meal["_id"] = str(meal["_id"])
        meal["source"] = "pending"
    return jsonify(pending_meals)

@admin_bp.route("/pending-meals/<meal_id>", methods=["PUT"])
@admin_required
def update_pending_meal(meal_id, current_user):
    data = request.get_json()

    servings = max(data.get("servings", 1), 1)
    ingredients = normalize_ingredients(data.get("ingredients", []), servings)

    data["ingredients"] = ingredients
    if isinstance(data.get("energy"), (int, float)):
        data["energy"] = int(round(data["energy"] / servings))
    if isinstance(data.get("price"), (int, float)):
        data["price"] = int(round(data["price"] / servings))

    data["servings"] = 1

    result = current_app.db.pending_meals.update_one(
        {"_id": ObjectId(meal_id)},
        {"$set": data}
    )
    if result.matched_count == 0:
        return jsonify({"message": "Không tìm thấy món ăn"}), 404
    return jsonify({"message": "Cập nhật món ăn thành công"}), 200


@admin_bp.route("/approve-meal/<meal_id>", methods=["POST"])
@admin_required
def approve_meal(meal_id, current_user):
    pending = current_app.db.pending_meals.find_one({"_id": ObjectId(meal_id)})
    if not pending:
        return jsonify({"message": "Không tìm thấy món ăn"}), 404

    # Chuyển sang collection chính
    new_meal = pending.copy()
    new_meal.pop("_id") 
    new_meal["createdAt"] = datetime.utcnow()
    new_meal["embedding"] = generate_meal_embedding(new_meal)
    current_app.db.meals.insert_one(new_meal)

    # Xóa khỏi pending
    current_app.db.pending_meals.delete_one({"_id": ObjectId(meal_id)})

    return jsonify({"message": "Duyệt món ăn thành công"})
    

@admin_bp.route("/reject-meal/<meal_id>", methods=["DELETE"])
@admin_required
def reject_meal(meal_id, current_user):
    result = current_app.db.pending_meals.delete_one({"_id": ObjectId(meal_id)})
    if result.deleted_count == 0:
        return jsonify({"message": "Không tìm thấy món ăn"}), 404
    return jsonify({"message": "Đã từ chối món ăn"}), 200





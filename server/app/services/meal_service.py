from flask import Blueprint, request, jsonify, current_app
from app.utils.similarity import suggest_similar_meals
from app.models.meal import Meal
from app.models.meal import serialize_meal
from app.models.meal_model import get_meals_by_type
from app.utils.meal_utils import meal_to_dict
from app.services.embedding_service import get_meal_embedding
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from bson import ObjectId
from fuzzywuzzy import fuzz
from unidecode import unidecode

# def suggest_meals(data):
#     all_meals = Meal.query.all()  # Lấy tất cả món ăn từ database
#     preferences = data.get("preferences", [])
    
#     # Lọc các món ăn phù hợp với sở thích và yêu cầu của người dùng
#     filtered_meals = [meal for meal in all_meals if any(tag in meal.tags for tag in preferences)]
    
#     suggestions = []
#     for meal in filtered_meals:
#         similar_meals = suggest_similar_meals(meal, filtered_meals)
#         suggestions.append({
#             "meal": meal.to_dict(),
#             "similar_meals": [m.to_dict() for m in similar_meals]
#         })
    
#     return suggestions

# def suggest_similar_meals(meal_id):
#     db = current_app.db
#     meals_collection = db.meals

#     # Lấy món mục tiêu
#     target_meal = meals_collection.find_one({"_id": ObjectId(meal_id)})
#     if not target_meal or "embedding" not in target_meal:
#         return []

#     target_vec = np.array(target_meal["embedding"]).reshape(1, -1)

#     # Lấy tất cả các món có embedding, trừ món hiện tại
#     other_meals = list(meals_collection.find({
#         "_id": {"$ne": ObjectId(meal_id)},
#         "embedding": {"$exists": True}
#     }))

#     # Tạo mảng vectors
#     other_vecs = np.array([m["embedding"] for m in other_meals])
#     similarities = cosine_similarity(target_vec, other_vecs)[0]
    
#     # Lấy top món tương tự nhất
#     top_indices = np.argsort(similarities)[::-1][:6]
#     similar_meals = [other_meals[i] for i in top_indices]

#     return [serialize_meal(m) for m in similar_meals]

# def suggest_similar_meals(meal_id):
#     db = current_app.db
#     meals_collection = db.meals

#     target_meal = meals_collection.find_one({"_id": ObjectId(meal_id)})
#     if not target_meal:
#         return []

#     all_meals = list(meals_collection.find({"_id": {"$ne": ObjectId(meal_id)}}))
#     target_tags = set(target_meal.get("tags", []))

#     def similarity(m):
#         tags = set(m.get("tags", []))
#         return len(tags & target_tags)

#     sorted_meals = sorted(all_meals, key=similarity, reverse=True)
#     return [serialize_meal(m) for m in sorted_meals[:6]]

def normalize_text(text):
    # Chuẩn hóa: bỏ dấu, chuyển thường, bỏ ký tự lạ
    text = unidecode(text)
    text = text.lower()
    return "".join(c for c in text if c.isalnum() or c.isspace())

def is_similar_name(name1, name2, threshold=70):
    # So sánh hai tên đã chuẩn hóa, trả về True nếu giống nhau trên ngưỡng
    return fuzz.token_sort_ratio(normalize_text(name1), normalize_text(name2)) >= threshold

def suggest_similar_meals(meal_id, allergens=None, calo_tolerance=0.3, price_tolerance=0.3, max_cal=None, max_price=None, top_k=6):
    db = current_app.db
    meals_collection = db.meals

    target_meal = meals_collection.find_one({"_id": ObjectId(meal_id)})
    if not target_meal:
        return []

    target_embedding = get_meal_embedding(target_meal)
    target_type = target_meal.get("type")
    target_cal = target_meal.get("energy", 0)
    target_price = target_meal.get("price", 0)

    min_cal = target_cal * (1 - calo_tolerance)
    max_cal = min(target_cal * (1 + calo_tolerance), max_cal or float('inf'))
    min_price = target_price * (1 - price_tolerance)
    max_price = min(target_price * (1 + price_tolerance), max_price or float('inf'))

    # min_cal, max_cal = target_cal * (1 - calo_tolerance), target_cal * (1 + calo_tolerance)
    # min_price, max_price = target_price * (1 - price_tolerance), target_price * (1 + price_tolerance)

    filter_query = {
        "_id": {"$ne": ObjectId(meal_id)},
        "type": target_type,
        "energy": {"$gte": min_cal, "$lte": max_cal},
        "price": {"$gte": min_price, "$lte": max_price}
    }
    if allergens:
        filter_query["allergens"] = {"$nin": allergens}
        # filter_query["allergens"] = {"$not": {"$elemMatch": {"$in": allergens}}}

    print("Mongo filter:", filter_query)

    candidates = list(meals_collection.find(filter_query))
    for meal in candidates:
        print("Allergens in candidate:", meal.get("allergens"))

    similarities = []
    for meal in candidates:
        embedding = get_meal_embedding(meal)
        if not embedding or len(embedding) == 0:
            print(f"[WARN] Empty embedding for meal: {meal.get('_id')}, skipping...")
            continue
        # sim_score = cosine_similarity([target_embedding], [embedding])[0][0]
        sim_score = cosine_similarity(
            np.array(target_embedding).reshape(1, -1),
            np.array(embedding).reshape(1, -1)
        )[0][0]
        similarities.append((sim_score, meal))

    # Sắp xếp theo độ tương đồng
    similarities.sort(key=lambda x: x[0], reverse=True)

    unique_results = []
    titles_seen = set()

    for sim_score, meal in similarities:
        meal_title = meal.get("title", "")
        if all(not is_similar_name(meal_title, seen) for seen in titles_seen):
            unique_results.append(serialize_meal(meal))
            titles_seen.add(meal_title)
        if len(unique_results) >= top_k:
            break
    # return [serialize_meal(m[1]) for m in similarities[:top_k]]
    return unique_results


# def toggle_snack_logic(current_main, current_snack):
#     target_calories = current_main["calories"]
#     target_price = current_main["price"]

#     all_main_meals = get_meals_by_type("main")

#     # Lọc ra các món chính mới thỏa điều kiện calorie và giá
#     valid_mains = [
#         meal for meal in all_main_meals
#         if meal["id"] != current_main["id"]
#         and meal["calories"] + current_snack["calories"] <= target_calories + 20
#         and meal["price"] + current_snack["price"] <= target_price + 5000
#     ]

#     if not valid_mains:
#         return current_main  # Không tìm được món chính phù hợp

#     # Tìm món chính có tổng calorie + giá gần nhất với món cũ
#     def diff_score(meal):
#         return abs((meal["calories"] + current_snack["calories"]) - target_calories) + \
#                abs((meal["price"] + current_snack["price"]) - target_price) / 1000

#     best_main = min(valid_mains, key=diff_score)

#     return best_main

# def toggle_snack_logic(current_main, preferences, allergens):
#     db = current_app.db

#     target_cal = current_main.get("original_calories", current_main["calories"])
#     target_price = current_main.get("original_cost", current_main["price"])

#     allowed_cal_margin = 0.15 * target_cal
#     allowed_price_margin = 0.15 * target_price

#     query = {"tags": {"$in": preferences}} if preferences else {}

#     if allergens:
#         query["$or"] = [
#             {"allergens": {"$exists": False}},
#             {"allergens": {"$eq": []}},
#             {"allergens": {"$not": {"$elemMatch": {"$in": allergens}}}}
#         ]
#     print("Mongo query:", query)

#     all_meals = list(db.meals.find(query))
#     print("Tổng số món lọc được:", len(all_meals))
#     current_main_id = current_main.get("id")
#     main_options = [m for m in all_meals if m["type"] == "main" and str(m["_id"]) != current_main_id]
#     snack_options = [m for m in all_meals if m["type"] == "snack"]

#     best_pair = None
#     min_error = float("inf")

#     for main in main_options:
#         for snack in snack_options:
#             total_cal = main.get("energy", 0) + snack.get("energy", 0)
#             total_price = main.get("price", 0) + snack.get("price", 0)

#             if abs(total_cal - target_cal) <= allowed_cal_margin and abs(total_price - target_price) <= allowed_price_margin:
#                 error = abs(total_cal - target_cal) + abs(total_price - target_price)
#                 if error < min_error:
#                     min_error = error
#                     best_pair = (main, snack)

#     if best_pair:
#         return {
#             "adjustedMain": meal_to_dict(best_pair[0], original_calories=target_cal, original_cost=target_price),
#             "adjustedSnack": meal_to_dict(best_pair[1])
#         }
#     else:
#         # fallback: giữ nguyên main, không có snack
#         return {
#             "adjustedMain": current_main,
#             "adjustedSnack": None
#         }

def toggle_snack_logic(current_main, preferences, allergens):
    db = current_app.db

    # Ngân sách còn lại là tổng - main
    total_cal = current_main.get("original_calories", current_main["calories"])
    total_price = current_main.get("original_cost", current_main["price"])
    main_cal = current_main["calories"]
    main_price = current_main["price"]

    remaining_cal = total_cal - main_cal
    remaining_price = total_price - main_price

    # Cho phép snack chênh lệch nhẹ
    allowed_cal = remaining_cal * 1.25
    allowed_price = remaining_price * 1.25

    # Query theo preferences
    query = {"type": "snack"}
    if preferences:
        query["tags"] = {"$in": preferences}
    
    if allergens:
        query["$or"] = [
            {"allergens": {"$exists": False}},
            {"allergens": {"$eq": []}},
            {"allergens": {"$not": {"$elemMatch": {"$in": allergens}}}}
        ]
    
    print("Mongo query:", query)

    snacks = list(db.meals.find(query))
    print("Số snack phù hợp:", len(snacks))

    valid_snacks = [
        s for s in snacks
        if s.get("energy", 0) <= allowed_cal and s.get("price", 0) <= allowed_price
    ]

    print("Số snack hợp lệ sau lọc:", len(valid_snacks))

    if valid_snacks:
        # Chọn snack gần nhất với lượng còn lại
        best_snack = min(
            valid_snacks,
            key=lambda s: abs(s.get("energy", 0) - remaining_cal) + abs(s.get("price", 0) - remaining_price)
        )
        return {
            "adjustedMain": current_main,
            "adjustedSnack": meal_to_dict(best_snack)
        }
    else:
        fallback_snack = min(
            snacks,
            key=lambda s: s.get("energy", 0) + s.get("price", 0)
        )
        return {
            "adjustedMain": current_main,
            "adjustedSnack": None #meal_to_dict(fallback_snack)
        }


def revert_main_only_logic(current_main, preferences, allergens):
    db = current_app.db

    target_cal = current_main.get("original_calories", current_main["calories"])
    target_price = current_main.get("original_cost", current_main["price"])

    allowed_cal_margin = 0.15 * target_cal
    allowed_price_margin = 0.15 * target_price

    query = {"type": "main"}
    if preferences:
        query["tags"] = {"$in": preferences}
    if allergens:
        query["$or"] = [
            {"allergens": {"$exists": False}},
            {"allergens": {"$eq": []}},
            {"allergens": {"$not": {"$elemMatch": {"$in": allergens}}}}
        ]

    current_main_id = current_main.get("id") or current_main.get("_id")
    main_options = [m for m in db.meals.find(query) if str(m["_id"]) != current_main_id]

    best_main = None
    min_error = float("inf")

    for main in main_options:
        cal = main.get("energy", 0)
        price = main.get("price", 0)

        if abs(cal - target_cal) <= allowed_cal_margin and abs(price - target_price) <= allowed_price_margin:
            error = abs(cal - target_cal) + abs(price - target_price)
            if error < min_error:
                min_error = error
                best_main = main

    if best_main:
        return {"revertedMain": meal_to_dict(best_main, original_calories=target_cal, original_cost=target_price)}
    else:
        return {"revertedMain": current_main} 

from flask import Blueprint, request, jsonify, current_app
from app.models.meal import Meal
import random
from app.utils.meal_utils import meal_to_dict
# from app.utils.similarity import suggest_similar_meals
from app.services.meal_service import toggle_snack_logic
from app.services.meal_service import suggest_similar_meals
from app.services.embedding_service import get_meal_embedding
from bson import ObjectId
from app.utils.token_utils import verify_token
from sklearn.metrics.pairwise import cosine_similarity

from collections import Counter
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
import json
from datetime import datetime
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

meals_bp = Blueprint("meals", __name__, url_prefix="/api/meals")


@meals_bp.route("/", methods=["GET"])
def get_all_meals():
    meals_cursor = current_app.db.meals.find()
    meals = [Meal(meal).to_dict() for meal in meals_cursor]
    return jsonify(meals), 200


# @meals_bp.route("/suggest", methods=["POST"])
# def suggest_meals():
#     data = request.json
#     budget = data.get("budget", 0)
#     constraint_type = data.get("constraint_type", "daily")
#     calories = data.get("calories", 0)
#     preferences = data.get("preferences", [])
#     allergens = data.get("allergens", [])
#     num_days = data.get("numDays", 1)
#     meal_times = data.get("mainMeals", ["sáng", "trưa", "tối"])

#     db = current_app.db

#     calorie_distribution = {
#         "Sáng": 0.2,
#         "Trưa": 0.4,
#         "Tối": 0.4
#     }

#     total_ratio = sum(calorie_distribution[m] for m in meal_times)
#     adjusted_distribution = {
#         m: calorie_distribution[m] / total_ratio for m in meal_times
#     }

#     # Lọc món phù hợp preferences và KHÔNG chứa allergens
#     query = {
#     "tags": {"$in": preferences}
#     }

#     if allergens:
#         query["$or"] = [
#             {"allergens": {"$exists": False}},
#             {"allergens": {"$eq": []}},
#             {"allergens": {"$not": {"$elemMatch": {"$in": allergens}}}}
#         ]

#     all_meals = list(db.meals.find(query))

#     if not all_meals:
#         return jsonify({"error": "Không tìm thấy món phù hợp"}), 404

#     enriched_meals = all_meals

#     # Auth
#     auth_header = request.headers.get("Authorization", "")
#     user_id = None
#     if auth_header.startswith("Bearer "):
#         token = auth_header.split(" ")[1]
#         user_id = verify_token(token)


#     if user_id:
#         user = current_app.db.users.find_one({"_id": ObjectId(user_id)})
#         if user:
#             # === Đã Login ===
#             print("📌 Đã login - user:", user["email"])
#             user_history = list(db.meal_histories.find({"user_id": user_id}))
#             user_meal_ids = {entry["id"] for entry in user_history}
#             user_meal_ids = set()
#             for entry in user_history:
#                 for daily_plan in entry.get("plan", []):
#                     for meal_time in ["Sáng", "Trưa", "Tối"]:
#                         meal_info = daily_plan.get(meal_time, {})
#                         for meal_type in ["main", "snack"]:
#                             meal = meal_info.get(meal_type)
#                             if meal and "id" in meal:
#                                 try:
#                                     user_meal_ids.add(ObjectId(meal["id"]))
#                                 except Exception as e:
#                                     print("⚠️ Lỗi khi chuyển meal id:", meal["id"], str(e))

#             user_meals = list(db.meals.find({"_id": {"$in": list(user_meal_ids)}}))

#             # Content-based filtering (dựa trên tags)
#             def tag_similarity(m1, m2):
#                 tags1 = set(m1.get("tags", []))
#                 tags2 = set(m2.get("tags", []))
#                 return len(tags1 & tags2) / (len(tags1 | tags2) + 1e-6)

#             similar_meals = []
#             for meal in all_meals:
#                 similarity = max(tag_similarity(meal, user_meal) for user_meal in user_meals)
#                 if similarity > 0.3:
#                     similar_meals.append((similarity, meal))

#             similar_meals.sort(reverse=True)
#             content_meals = [m for _, m in similar_meals[:100]]

#             # Collaborative filtering: tìm người dùng khác ăn các món giống bạn
#             similar_users = db.meal_histories.aggregate([
#                 {"$match": {
#                     "$or": [
#                         {"plan.Sáng.main.id": {"$in": [str(_id) for _id in user_meal_ids]}},
#                         {"plan.Sáng.snack.id": {"$in": [str(_id) for _id in user_meal_ids]}},
#                         {"plan.Trưa.main.id": {"$in": [str(_id) for _id in user_meal_ids]}},
#                         {"plan.Trưa.snack.id": {"$in": [str(_id) for _id in user_meal_ids]}},
#                         {"plan.Tối.main.id": {"$in": [str(_id) for _id in user_meal_ids]}},
#                         {"plan.Tối.snack.id": {"$in": [str(_id) for _id in user_meal_ids]}}
#                     ],
#                     "user_id": {"$ne": user_id}
#                 }},
#                 {"$group": {"_id": "$user_id"}}
#             ])
#             similar_user_ids = [u["_id"] for u in similar_users]

#             collaborative_meal_ids = set()
#             if similar_user_ids:
#                 history_from_similar_users = db.meal_histories.find({"user_id": {"$in": similar_user_ids}})
#                 for entry in history_from_similar_users:
#                     for daily_plan in entry.get("plan", []):
#                         for meal_time in ["Sáng", "Trưa", "Tối"]:
#                             meal_info = daily_plan.get(meal_time, {})
#                             for meal_type in ["main", "snack"]:
#                                 meal = meal_info.get(meal_type)
#                                 if meal and "id" in meal:
#                                     try:
#                                         collaborative_meal_ids.add(ObjectId(meal["id"]))
#                                     except:
#                                         pass

#             collaborative_meals = list(db.meals.find({"_id": {"$in": list(collaborative_meal_ids)}}))

#             # Kết hợp kết quả, loại trùng
#             all_meals_dict = {str(m["_id"]): m for m in all_meals}
#             content_dict = {str(m["_id"]): m for m in content_meals}
#             collab_dict = {str(m["_id"]): m for m in collaborative_meals}
#             enriched_meals = list({**all_meals_dict, **content_dict, **collab_dict}.values())
#         else:
#             print("❌ Token đúng nhưng không tìm thấy user")
#     else:
#         print("👤 Người dùng chưa đăng nhập")

#     # Chọn món
#     def sort_meals_by_calorie_and_price(meals, target_cal):
#         return sorted(meals, key=lambda m: (abs(m["energy"] - target_cal), m["price"]))

#     def score_meal(meal, target_cal):
#         return abs(meal["energy"] - target_cal) + 0.3 * meal["price"]

#     def sort_meals_by_score(meals, target_cal):
#         return sorted(meals, key=lambda m: score_meal(m, target_cal))

#     def select_random_top_n(sorted_meals, top_n=6, budget_left=None):
#         top = sorted_meals[:top_n]
#         if budget_left is not None:
#             top = [m for m in top if m["price"] <= budget_left]
#         return random.choice(top) if top else None

#     def is_valid_energy(meal_energy, target_cal):
#         min_cal = target_cal * 0.7
#         max_cal = target_cal * 1.3
#         return min_cal <= meal_energy <= max_cal

#     suggestions = []

#     if constraint_type == "daily":
#         recent_meal_history = []
#         for _ in range(num_days):
#             daily_plan = {}
#             daily_cost = 0
#             daily_used_ids = set()
#             banned_ids = set()
#             for recent_day in recent_meal_history[-2:]:
#                 banned_ids.update(recent_day)

#             for meal_time in meal_times:
#                 meal_calo_target = calories * calorie_distribution[meal_time]

#                 # Chọn main
#                 main_options = [
#                     m for m in enriched_meals if m["type"] == "main" 
#                     and m["_id"] not in banned_ids 
#                     and m["_id"] not in daily_used_ids
#                     and is_valid_energy(m["energy"], meal_calo_target)
#                 ]
#                 sorted_main = sort_meals_by_score(main_options, meal_calo_target)
#                 selected_main = select_random_top_n(sorted_main, top_n=20, budget_left=budget - daily_cost)

#                 #hàm cũ
#                 # selected_main = next(
#                 #     (m for m in main_options
#                 #      if m["price"] + daily_cost <= budget and
#                 #         is_valid_energy(m["energy"], meal_calo_target)),
#                 #     None
#                 # )
                
#                 # if not selected_main:
#                 #     selected_main = next(
#                 #         (m for m in sorted(main_options, key=lambda m: m["price"])
#                 #         if m["price"] + daily_cost <= budget),
#                 #         None
#                 #     )
#                 #-----------------------------------                           


#                 if not selected_main:
#                     return jsonify({"error": f"Không tìm được món chính cho bữa {meal_time}"}), 400

#                 daily_cost += selected_main["price"]
#                 daily_used_ids.add(selected_main["_id"])

#                 daily_plan[meal_time] = {
#                     "main": meal_to_dict(
#                         selected_main,
#                         original_calories=selected_main["energy"],
#                         original_cost=selected_main["price"]
#                     ),
#                     "snack": None
#                 }

#             suggestions.append(daily_plan)
#             recent_meal_history.append(daily_used_ids)

#     else:  # constraint_type == "total"
#         max_attempts = 100
#         for _ in range(max_attempts):
#             temp_suggestions = []
#             total_cost = 0
#             valid_plan = True
#             recent_meal_history = []

#             for _ in range(num_days):
#                 daily_plan = {}
#                 daily_day_cost = 0
#                 daily_used_ids = set()
#                 banned_ids = set()
#                 for recent_day in recent_meal_history[-3:]:
#                     banned_ids.update(recent_day)

#                 for meal_time in meal_times:
#                     meal_calo_target = calories * calorie_distribution[meal_time]

#                     main_options = [
#                         m for m in enriched_meals if m["type"] == "main" 
#                         and m["_id"] not in banned_ids 
#                         and m["_id"] not in daily_used_ids
#                         and is_valid_energy(m["energy"], meal_calo_target)
#                     ]
#                     sorted_main = sort_meals_by_score(main_options, meal_calo_target)
#                     selected_main = select_random_top_n(sorted_main, top_n=20, budget_left=budget - total_cost)

#                     #hàm cũ
#                     # selected_main = next(
#                     #     (m for m in main_options
#                     #      if m["price"] + total_cost <= budget and
#                     #         is_valid_energy(m["energy"], meal_calo_target)),
#                     #     None
#                     # )

#                     # if not selected_main:
#                     #     selected_main = next(
#                     #         (m for m in sorted(main_options, key=lambda m: m["price"])
#                     #         if m["price"] + total_cost <= budget),
#                     #         None
#                     #     )
#                     #-------------------

#                     if not selected_main:
#                         valid_plan = False
#                         break
                    
#                     total_cost += selected_main["price"]
#                     daily_used_ids.add(selected_main["_id"])

#                     daily_plan[meal_time] = {
#                         "main": meal_to_dict(
#                             selected_main,
#                             original_calories=selected_main["energy"],
#                             original_cost=selected_main["price"]
#                         ),
#                         "snack": None
#                     }

#                 if not valid_plan or len(daily_plan) < len(meal_times):
#                     break

#                 temp_suggestions.append(daily_plan)
#                 recent_meal_history.append(daily_used_ids)

#             if valid_plan and len(temp_suggestions) == num_days and total_cost <= budget:
#                 suggestions = temp_suggestions
#                 break

#         #hàm check            
#         # print("valid_plan:", valid_plan)
#         # print("num_days:", num_days, "temp_suggestions:", len(temp_suggestions))
#         # print("total_cost:", total_cost, "budget:", budget)
#         #-----------------------------

#         if not suggestions:
#             return jsonify({"error": "Không thể tạo đủ 3 bữa mỗi ngày trong giới hạn ngân sách"}), 400

#     return jsonify(suggestions), 200

# @meals_bp.route("/suggest", methods=["POST"])
# def suggest_meals():
#     data = request.json
#     budget = data.get("budget", 0)
#     constraint_type = data.get("constraint_type", "daily")
#     calories = data.get("calories", 0)
#     preferences = data.get("preferences", [])
#     allergens = data.get("allergens", [])
#     num_days = data.get("numDays", 1)
#     meal_times = data.get("mainMeals", ["Sáng", "Trưa", "Tối"])

#     db = current_app.db

#     calorie_distribution = {
#         "Sáng": 0.2,
#         "Trưa": 0.4,
#         "Tối": 0.4
#     }

#     total_ratio = sum(calorie_distribution[m] for m in meal_times)
#     adjusted_distribution = {m: calorie_distribution[m] / total_ratio for m in meal_times}

#     # Tìm món phù hợp preferences và không dị ứng
#     query = {"tags": {"$in": preferences}}
#     if allergens:
#         query["$or"] = [
#             {"allergens": {"$exists": False}},
#             {"allergens": {"$eq": []}},
#             {"allergens": {"$not": {"$elemMatch": {"$in": allergens}}}}
#         ]

#     all_meals = list(db.meals.find(query))
#     if not all_meals:
#         return jsonify({"error": "Không tìm thấy món phù hợp"}), 404

#     enriched_meals = all_meals

#     # Nếu có user login thì áp dụng lọc lịch sử ăn
#     user_id = None
#     token = request.headers.get("Authorization", "").replace("Bearer ", "")
#     if token:
#         user_id = verify_token(token)

#     if user_id:
#         user_history = list(db.meal_histories.find({"user_id": user_id}))
#         user_meal_ids = set()
#         for entry in user_history:
#             for day in entry.get("plan", []):
#                 for meal_time in ["Sáng", "Trưa", "Tối"]:
#                     meal_info = day.get(meal_time, {})
#                     for mtype in ["main", "snack"]:
#                         meal = meal_info.get(mtype)
#                         if meal and "id" in meal:
#                             try:
#                                 user_meal_ids.add(ObjectId(meal["id"]))
#                             except:
#                                 pass
#         user_meals = list(db.meals.find({"_id": {"$in": list(user_meal_ids)}}))

#         # def tag_similarity(m1, m2):
#         #     t1, t2 = set(m1.get("tags", [])), set(m2.get("tags", []))
#         #     return len(t1 & t2) / (len(t1 | t2) + 1e-6)
        
#         # def ingredient_similarity(m1, m2):
#         #     ing1 = set(i.get("name", "").lower() for i in m1.get("ingredients", []))
#         #     ing2 = set(i.get("name", "").lower() for i in m2.get("ingredients", []))
#         #     return len(ing1 & ing2) / (len(ing1 | ing2) + 1e-6)

#         # def content_similarity(m1, m2):
#         #     tag_sim = tag_similarity(m1, m2)
#         #     ing_sim = ingredient_similarity(m1, m2)
#         #     return 0.5 * tag_sim + 0.5 * ing_sim

#         def embedding_similarity(m1, m2):
#             e1 = get_meal_embedding(m1)
#             e2 = get_meal_embedding(m2)
#             return cosine_similarity([e1], [e2])[0][0]

#         # content_meals = [
#         #     m for _, m in sorted(
#         #         [(max(content_similarity(m, um) for um in user_meals), m)
#         #          for m in all_meals if user_meals],
#         #         reverse=True
#         #     )[:100]
#         # ]

#         # content_meals = [
#         #     m for _, m in sorted(
#         #         [(max(embedding_similarity(m, um) for um in user_meals), m)
#         #         for m in all_meals if user_meals],
#         #         reverse=True
#         #     )[:100]
#         # ]

#         user_texts = [
#             get_meal_embedding(meal) or "unknown"
#             for meal in user_meals
#         ]
#         print(">>> user_texts:", user_texts)
#         print(">>> types:", [type(t) for t in user_texts])
#         all_texts = [get_meal_embedding(m) for m in all_meals]

#         user_embeddings = model.encode(user_texts, convert_to_numpy=True, show_progress_bar=False)
#         all_embeddings = model.encode(all_texts, convert_to_numpy=True, show_progress_bar=False)

#         # Tính cosine_similarity matrix (all x user)
#         sim_matrix = cosine_similarity(all_embeddings, user_embeddings)
#         max_similarities = sim_matrix.max(axis=1)

#         # Ghép mỗi món với điểm tương đồng cao nhất
#         scored_meals = list(zip(max_similarities, all_meals))

#         # Lấy top 100 món gần nhất
#         scored_meals.sort(reverse=True, key=lambda x: x[0])
#         content_meals = [m for _, m in scored_meals[:100]]

#         similar_users = db.meal_histories.aggregate([
#             {"$match": {
#                 "$or": [
#                     {"plan.Sáng.main.id": {"$in": [str(i) for i in user_meal_ids]}},
#                     {"plan.Sáng.snack.id": {"$in": [str(i) for i in user_meal_ids]}},
#                     {"plan.Trưa.main.id": {"$in": [str(i) for i in user_meal_ids]}},
#                     {"plan.Trưa.snack.id": {"$in": [str(i) for i in user_meal_ids]}},
#                     {"plan.Tối.main.id": {"$in": [str(i) for i in user_meal_ids]}},
#                     {"plan.Tối.snack.id": {"$in": [str(i) for i in user_meal_ids]}}
#                 ],
#                 "user_id": {"$ne": user_id}
#             }},
#             {"$group": {"_id": "$user_id"}}
#         ])
#         similar_ids = [u["_id"] for u in similar_users]

#         collab_ids = set()
#         for h in db.meal_histories.find({"user_id": {"$in": similar_ids}}):
#             for d in h.get("plan", []):
#                 for t in ["Sáng", "Trưa", "Tối"]:
#                     for k in ["main", "snack"]:
#                         meal = d.get(t, {}).get(k)
#                         if meal and "id" in meal:
#                             try:
#                                 collab_ids.add(ObjectId(meal["id"]))
#                             except:
#                                 pass

#         collaborative_meals = list(db.meals.find({"_id": {"$in": list(collab_ids)}}))

#         enriched_meals = list({
#             str(m["_id"]): m
#             for m in all_meals + content_meals + collaborative_meals
#         }.values())
#         random.shuffle(enriched_meals)

#     def is_valid_energy(val, target):
#         return target * 0.9 <= val <= target * 1.2

#     def score_meal(meal, target):
#         noise = random.uniform(-5, 5)
#         return abs(meal["energy"] - target) + 0.3 * meal["price"] + noise

#     def select_random_top_n(sorted_list, top_n, budget_left):
#         top = [m for m in sorted_list[:top_n] if m["price"] <= budget_left]
#         return random.choice(top) if top else None

#     suggestions = []

#     def pick_main_and_snack(meal_time, meal_calo_target, budget_left, enriched_meals, banned_ids, used_ids):
#         main_options = [
#             m for m in enriched_meals if m["type"] == "main"
#             and m["_id"] not in banned_ids
#             and m["_id"] not in used_ids
#         ]
#         snack_options = [
#             m for m in enriched_meals if m["type"] == "snack"
#             and m["_id"] not in banned_ids
#             and m["_id"] not in used_ids
#         ]

#         best_combo = None
#         valid_combos = []
#         min_score = float("inf")

#         for main in main_options:
#             for snack in snack_options:
#                 total_energy = main["energy"] + snack["energy"]
#                 total_price = main["price"] + snack["price"]
#                 if total_price <= budget_left and is_valid_energy(total_energy, meal_calo_target):
#                     score = score_meal(main, meal_calo_target * 0.7) + score_meal(snack, meal_calo_target * 0.3)
#                     valid_combos.append((score, (main, snack)))
#         valid_combos.sort(key=lambda x: x[0])
#         top_combos = valid_combos[:15]
#         if top_combos:
#             best_combo = random.choice(top_combos)[1]

#         # Nếu không tìm được combo hợp lệ thì thử chỉ lấy món chính
#         if not best_combo:
#             sorted_main = sort_meals_by_score(main_options, meal_calo_target)
#             main = select_random_top_n(sorted_main, top_n=30, budget_left=budget_left)
#             if main and is_valid_energy(main["energy"], meal_calo_target):
#                 return main, None

#         return best_combo if best_combo else (None, None)

#     if constraint_type == "daily":
#         recent_meal_history = []
#         for _ in range(num_days):
#             daily_plan = {}
#             daily_cost = 0
#             daily_used_ids = set()
#             banned_ids = set()
#             for recent_day in recent_meal_history[-2:]:
#                 banned_ids.update(recent_day)

#             for meal_time in meal_times:
#                 meal_calo_target = calories * calorie_distribution[meal_time]
#                 main, snack = pick_main_and_snack(
#                     meal_time, meal_calo_target, budget - daily_cost,
#                     enriched_meals, banned_ids, daily_used_ids
#                 )

#                 if not main:
#                     return jsonify({"error": f"Không tìm được món phù hợp cho bữa {meal_time}"}), 400

#                 daily_cost += main["price"]
#                 if snack:
#                     daily_cost += snack["price"]
#                     daily_used_ids.add(snack["_id"])

#                 daily_used_ids.add(main["_id"])

#                 daily_plan[meal_time] = {
#                     "main": meal_to_dict(main, original_calories=main["energy"], original_cost=main["price"]),
#                     "snack": meal_to_dict(snack, original_calories=snack["energy"], original_cost=snack["price"]) if snack else None
#                 }

#             suggestions.append(daily_plan)
#             recent_meal_history.append(daily_used_ids)

#     else:  # constraint_type == "total"
#         max_attempts = 100
#         for _ in range(max_attempts):
#             temp_suggestions = []
#             total_cost = 0
#             valid_plan = True
#             recent_meal_history = []

#             for _ in range(num_days):
#                 daily_plan = {}
#                 daily_used_ids = set()
#                 banned_ids = set()
#                 for recent_day in recent_meal_history[-2:]:
#                     banned_ids.update(recent_day)

#                 for meal_time in meal_times:
#                     meal_calo_target = calories * calorie_distribution[meal_time]
#                     main, snack = pick_main_and_snack(
#                         meal_time, meal_calo_target, budget - total_cost,
#                         enriched_meals, banned_ids, daily_used_ids
#                     )

#                     if not main:
#                         valid_plan = False
#                         break

#                     daily_used_ids.add(main["_id"])
#                     total_cost += main["price"]

#                     if snack:
#                         daily_used_ids.add(snack["_id"])
#                         total_cost += snack["price"]

#                     daily_plan[meal_time] = {
#                         "main": meal_to_dict(main, original_calories=main["energy"], original_cost=main["price"]),
#                         "snack": meal_to_dict(snack, original_calories=snack["energy"], original_cost=snack["price"]) if snack else None
#                     }

#                 if not valid_plan or len(daily_plan) < len(meal_times):
#                     break

#                 temp_suggestions.append(daily_plan)
#                 recent_meal_history.append(daily_used_ids)

#             if valid_plan and len(temp_suggestions) == num_days and total_cost <= budget:
#                 suggestions = temp_suggestions
#                 break

#         if not suggestions:
#             return jsonify({"error": "Không thể tạo đủ 3 bữa mỗi ngày trong giới hạn ngân sách"}), 400

#     return jsonify(suggestions), 200
    


def get_user_ingredient_vector(user_meal_ids, meals_collection, all_ingredient_names):
    vector = np.zeros(len(all_ingredient_names))
    name_to_idx = {name: i for i, name in enumerate(all_ingredient_names)}
    
    for meal in meals_collection.find({"_id": {"$in": list(user_meal_ids)}}):
        for ing in meal.get("ingredients", []):
            name = ing.get("name", "")
            if name in name_to_idx:
                vector[name_to_idx[name]] += 1
    return vector

@meals_bp.route("/suggest", methods=["POST"])
def suggest_meals():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    print(">>> Token received:", token)
    print(">>> /suggest endpoint hit")
    data = request.json
    budget = data.get("budget", 0)
    constraint_type = data.get("constraint_type", "daily")
    calories = data.get("calories", 0)
    preferences = data.get("preferences", [])
    allergens = data.get("allergens", [])
    num_days = data.get("numDays", 1)
    meal_times = data.get("mainMeals", ["Sáng", "Trưa", "Tối"])

    db = current_app.db

    calorie_distribution = {
        "Sáng": 0.2,
        "Trưa": 0.4,
        "Tối": 0.4
    }

    total_ratio = sum(calorie_distribution[m] for m in meal_times)
    adjusted_distribution = {m: calorie_distribution[m] / total_ratio for m in meal_times}

    # Tìm món phù hợp preferences và không dị ứng
    query = {"tags": {"$in": preferences}}
    if allergens:
        query["$or"] = [
            {"allergens": {"$exists": False}},
            {"allergens": {"$eq": []}},
            {"allergens": {"$not": {"$elemMatch": {"$in": allergens}}}}
        ]

    all_meals = list(db.meals.find(query))
    if not all_meals:
        return jsonify({"error": "Không tìm thấy món phù hợp"}), 404
    
    print("Sample meal:", all_meals[0].get("embedding"))
    print("Has embedding:", [m["_id"] for m in all_meals if "embedding" in m])

    fallback_meals = []
    for m in all_meals:
        m_copy = m.copy()
        m_copy["score"] = 0.1
        fallback_meals.append(m_copy)

    enriched_meals = fallback_meals.copy()


    # === Collaborative Filtering - Clustering theo ingredient vector ===
    # def extract_meal_ids(plan, target_calories=None):
    #     meal_ids = set()
    #     for day in plan:
    #         total_day_calories = 0
    #         day_meals = []
    #         for meal_time in ["Sáng", "Trưa", "Tối"]:
    #             meal_info = day.get(meal_time, {})
    #             for mtype in ["main", "snack"]:
    #                 meal = meal_info.get(mtype)
    #                 if meal and "id" in meal:
    #                     try:
    #                         meal_ids.add(ObjectId(meal["id"]))
    #                         day_meals.append(meal)
    #                         total_day_calories += meal.get("energy", 0)
    #                     except:
    #                         pass
    #         if target_calories and not (target_calories * 0.9 <= total_day_calories <= target_calories * 1.1):
    #             for meal in day_meals:
    #                 meal_ids.discard(ObjectId(meal["id"]))
    #     return list(meal_ids)

    # all_ingredient_names = sorted({ing["name"] for m in db.meals.find() for ing in m.get("ingredients", [])})
    # all_ingredient_names = db.meals.distinct("ingredients.name")

    # user_vectors = []
    # user_ids = []
    # for user_doc in db.meal_histories.find().limit(1000):
    #     user_id = user_doc["user_id"]
    #     user_meal_ids = extract_meal_ids(user_doc["plan"], target_calories=calories)
    #     vec = get_user_ingredient_vector(user_meal_ids, db.meals, all_ingredient_names)
    #     if np.sum(vec) > 0:
    #         user_vectors.append(vec)
    #         user_ids.append(user_id)

    # user_vectors = normalize(np.array(user_vectors))
    # n_clusters = min(20, len(user_vectors)) if len(user_vectors) >= 2 else 1
    # kmeans = KMeans(n_clusters=n_clusters)
    # labels = kmeans.fit_predict(user_vectors)
    # user_id_to_cluster = dict(zip(user_ids, labels))


    # ===== Nếu có user login thì thêm collaborative & content-based filtering =====
    user_id = None
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    print(">>> Token received:", token)
    if token:
        user_id = verify_token(token)
        print(">>> Decoded user_id:", user_id)
    if user_id is not None:
        user_history = list(db.meal_histories.find({"user_id": user_id}))
        user_meal_ids = set()
        for entry in user_history:
            for day in entry.get("plan", []):
                for meal_time in ["Sáng", "Trưa", "Tối"]:
                    meal_info = day.get(meal_time, {})
                    for mtype in ["main", "snack"]:
                        meal = meal_info.get(mtype)
                        if meal and "id" in meal:
                            try:
                                user_meal_ids.add(ObjectId(meal["id"]))
                            except:
                                pass
        used_meal_ids = set(user_meal_ids)
        used_meals = [meal for meal in all_meals if meal["_id"] in used_meal_ids]
        user_meals = list(db.meals.find({"_id": {"$in": list(user_meal_ids)}}))


        # Content-based filtering: chọn món dựa trên embedding similarity với user meals
        # def embedding_similarity(m1, m2):
        #     e1 = get_meal_embedding(m1)
        #     e2 = get_meal_embedding(m2)
        #     return cosine_similarity([e1], [e2])[0][0]

        # content_meals = [
        #     m for _, m in sorted(
        #         [(max(embedding_similarity(m, um) for um in user_meals), m)
        #         for m in all_meals if user_meals],
        #         reverse=True
        #     )[:100]
        # ]

        # user_texts = [
        #     get_meal_embedding(meal) or "unknown"
        #     for meal in user_meals
        # ]
        # print(">>> user_texts:", user_texts)
        # print(">>> types:", [type(t) for t in user_texts])
        # all_texts = [get_meal_embedding(m) for m in all_meals]

        # user_embeddings = model.encode(user_texts, convert_to_numpy=True, show_progress_bar=False)
        # all_embeddings = model.encode(all_texts, convert_to_numpy=True, show_progress_bar=False)

        user_embeddings_list = [meal["embedding"] for meal in user_meals if "embedding" in meal]
        user_meals = [
            m for m in user_meals
            if 0.6 * calories <= m.get("energy", 0) <= 1.4 * calories
        ]

        all_embeddings_list = [m.get("embedding") for m in all_meals if m.get("embedding")]

        # Nếu không có embedding từ user => bỏ qua content-based filtering
        if not user_embeddings_list or not all_embeddings_list:
            content_meals = []  # fallback về empty
        else:
            user_embeddings = np.array(user_embeddings_list).reshape(len(user_embeddings_list), -1)
            all_embeddings = np.array(all_embeddings_list).reshape(len(all_embeddings_list), -1)

            # Tính cosine_similarity matrix (all x user)
            sim_matrix = cosine_similarity(all_embeddings, user_embeddings)
            max_similarities = sim_matrix.max(axis=1)

            # Ghép mỗi món với điểm tương đồng cao nhất
            scored_meals = list(zip(max_similarities, all_meals))
            # Lấy top 100 món gần nhất
            scored_meals.sort(reverse=True, key=lambda x: x[0])
            # content_meals = [m for _, m in scored_meals[:100]]
            top_similar = [m for m in scored_meals if m[0] >= 0.8][:50]
            mid_similar_pool = [m for m in scored_meals if 0.75 <= m[0] < 0.9]
            mid_similar = random.sample(mid_similar_pool, min(len(mid_similar_pool), 20))
            combined_meals = top_similar + mid_similar
            random.shuffle(combined_meals)
            content_meals = []
            # for sim, m in scored_meals[:100]:
            #     m_copy = m.copy()
            #     noise = random.uniform(0, 0.02)
            #     m_copy["score"] = float(sim - noise)
            #     content_meals.append(m_copy)
            for sim, m in combined_meals:
                m_copy = m.copy()
                base_score = float(sim)
                novelty_bonus = 0.4 if m_copy["_id"] not in used_meal_ids else 0.0
                diversity_bonus = 0.15 if sim <= 0.85 else 0.0
                random_bonus = random.uniform(0, 0.03)
                m_copy["score"] = 0.5 * base_score + 0.3 * novelty_bonus + 0.15 * diversity_bonus + 0.05 * random_bonus
                content_meals.append(m_copy)
            content_meals_new = [m for m in content_meals if m["_id"] not in used_meal_ids]
            content_meals_used = [m for m in content_meals if m["_id"] in used_meal_ids]

        # Collaborative filtering: chọn user cùng cluster
        user_doc = db.meal_histories.find_one({"user_id": user_id})
        cluster_label = user_doc.get("cluster_id") if user_doc else None
        # cluster_label = db.meal_histories.find_one({"user_id": user_id}).get("cluster_id")
        if cluster_label is None:
            logger.warning(f"User {user_id} chưa được gán cluster_id.")
            similar_user_ids = []
        else:
            similar_user_ids = list({
            uid_doc["user_id"]
            for uid_doc in db.meal_histories.find({
                "cluster_id": cluster_label,
                "user_id": {"$ne": user_id}
            })
        })
        print(f"Cluster label: {cluster_label} - Found {len(similar_user_ids)} similar users")

        # similar_user_ids = [
        #     uid for uid, cl in user_id_to_cluster.items()
        #     if cl == cluster_label and uid != user_id
        # ]
        # similar_user_ids = [h["user_id"] for h in db.meal_histories.find({"cluster_id": cluster_label, "user_id": {"$ne": user_id}})]

        collaborative_meals = []
        collaborative_meals_raw = []
        collab_ids = set()
        if len(similar_user_ids) < 2:
            print("Cluster quá nhỏ, bỏ qua collaborative filtering.")
        else:
            for h in db.meal_histories.find({"user_id": {"$in": similar_user_ids}}):
                for d in h.get("plan", []):
                    for t in ["Sáng", "Trưa", "Tối"]:
                        for k in ["main", "snack"]:
                            meal = d.get(t, {}).get(k)
                            if meal and "id" in meal:
                                try:
                                    meal_detail = db.meals.find_one({"_id": ObjectId(meal["id"])})
                                    if meal_detail:
                                        if 0.6 * calories <= meal_detail.get("energy", 0) <= 1.4 * calories:
                                            collab_ids.add(meal_detail["_id"])
                                except Exception as e:
                                    print("Error fetching meal:", e)
                    
            print("Collected collaborative meal IDs:", list(collab_ids))        

            collaborative_meals_raw = list(db.meals.find({"_id": {"$in": list(collab_ids)},
                                                    "energy": {"$gte": 0.6 * calories, "$lte": 1.4 * calories}}))
            print("Collaborative meals found:", len(collaborative_meals_raw))
            # collab_scores = [(str(m["_id"]), m["title"]) for m in collaborative_meals]
            for m in collaborative_meals_raw:
                m_copy = m.copy()
                base_score = 0.85 + random.uniform(0, 0.05)
                novelty_bonus = 0.4 if m_copy["_id"] not in used_meal_ids else 0.0 
                random_bonus = random.uniform(0, 0.05)
                diversity_bonus = 0.1
                if not used_meals:
                    diversity_bonus = 0.1
                if m_copy.get("embedding") is not None and used_meals:
                    similarities = cosine_similarity(
                        [m_copy["embedding"]],
                        [meal["embedding"] for meal in used_meals if meal.get("embedding") is not None]
                    )
                    max_sim = similarities.max() if similarities.size > 0 else 0
                    diversity_bonus = 0.15 if max_sim <= 0.85 else 0.05

                random_bonus = random.uniform(0, 0.03)

                m_copy["score"] = 0.5 * base_score + 0.3 * novelty_bonus + 0.15 * diversity_bonus +0.05 * random_bonus
                collaborative_meals.append(m_copy)

        if not collaborative_meals and len(similar_user_ids) >= 1:
            print("Không tìm thấy món collaborative phù hợp. Sử dụng fallback: món phổ biến nhất trong cluster.")

            meal_counter = Counter()
            for h in db.meal_histories.find({"user_id": {"$in": similar_user_ids}}):
                for d in h.get("plan", []):
                    for t in ["Sáng", "Trưa", "Tối"]:
                        for k in ["main", "snack"]:
                            meal = d.get(t, {}).get(k)
                            if meal and "id" in meal:
                                try:
                                    meal_counter[meal["id"]] += 1
                                except:
                                    continue

            popular_ids = [ObjectId(mid) for mid, _ in meal_counter.most_common(15)]
            popular_meals = list(db.meals.find({"_id": {"$in": popular_ids}}))
            for m in popular_meals:
                m["score"] = 0.9
            collaborative_meals = popular_meals
            print(f"Used fallback popular meals in cluster: {len(collaborative_meals)}")
        collaborative_meals_new = [m for m in collaborative_meals if m["_id"] not in used_meal_ids]
        collaborative_meals_used = [m for m in collaborative_meals if m["_id"] in used_meal_ids]
        # random.shuffle(collaborative_meals)
        # for m in collaborative_meals:
        #     m["score"] = 0.95 + random.uniform(0, 0.05)

        # collaborative_meals = [{"_id": m["_id"], "title": m["title"]} for m in collaborative_meals]

        # merged = fallback_meals + content_meals + collaborative_meals
        # random.shuffle(content_meals_new)
        # random.shuffle(collaborative_meals_new)
        def multiply_list(lst, weight):
            if weight <= 0:
                return []
            n = int(weight)
            frac = weight - n
            result = lst * n
            if frac > 0 and len(lst) > 0:
                extra_num = max(1, int(len(lst) * frac))
                extra = random.sample(lst, min(extra_num, len(lst)))
                result += extra
            return result
        
        if len(user_meals) < 5:
            content_weight = 1.5
            collab_weight = 0.8
        else:
            content_weight = 1.0
            collab_weight = 1.1

        merged = (
            multiply_list(content_meals_new, content_weight) +
            multiply_list(collaborative_meals_new, collab_weight) +
            multiply_list(content_meals_used, 0.8) +
            multiply_list(collaborative_meals_used, 0.8) +
            fallback_meals
        )

        merged_dict = {}
        for m in merged:
            mid = str(m["_id"])
            if mid not in merged_dict or m["score"] > merged_dict[mid]["score"]:
                merged_dict[mid] = m
        enriched_meals = sorted(merged_dict.values(), key=lambda m: m["score"], reverse=True)

        diversity_pool = enriched_meals[:200]
        remaining_pool = enriched_meals[200:]

        final_enriched = []
        seen_tokens = []
        embedding_seen = []
        def is_too_similar(title_tokens, seen_tokens, threshold=2):
            return any(len(title_tokens & prev) >= threshold for prev in seen_tokens)
        
        def is_embedding_too_similar(embed1, embed_list, threshold=0.8):
            return any(cosine_similarity([embed1], [e])[0][0] >= threshold for e in embed_list)

        for m in diversity_pool:
            embed = m.get("embedding")
            title_tokens = set(m["title"].lower().split())
            # if any(len(title_tokens & prev) >= 3 for prev in seen_tokens):
            #     continue
            if is_too_similar(title_tokens, seen_tokens, threshold=2):
                continue
            if embed is not None and is_embedding_too_similar(embed, embedding_seen, threshold=0.8):
                continue
            seen_tokens.append(title_tokens)
            if embed is not None:
                embedding_seen.append(embed)
            final_enriched.append(m)
            if len(final_enriched) >= 27:
                break

        if user_embeddings_list:
            user_mean_embed = np.mean(user_embeddings_list, axis=0)
            serendipity_pool = []
            for m in enriched_meals:
                embed = m.get("embedding")
                if embed is None:
                    continue
                sim = cosine_similarity([embed], [user_mean_embed])[0][0]
                serendipity_pool.append((sim, m))

            serendipity_pool.sort(key=lambda x: x[0])  # Cos thấp nhất
            serendipity_meals = [m for _, m in serendipity_pool[:3]]
            for m in serendipity_meals:
                m["score"] += 0.15
            final_enriched.extend(serendipity_meals)

        if len(final_enriched) < 30:
            missing = 30 - len(final_enriched)
            candidates = [
                m for m in remaining_pool
                if set(m["title"].lower().split()) not in seen_tokens
            ]
            random.shuffle(candidates)
            final_enriched.extend(candidates[:missing])

        # Ghép lại toàn bộ enriched_meals đã đa dạng hóa trước
        enriched_meals = final_enriched + [m for m in remaining_pool if m not in final_enriched]
        print("Tổng số món enriched_meals sau diversity filter:", len(enriched_meals))

        for m in enriched_meals[:30]:
            print(m["title"], m["score"])
        print("Fallback:", len(fallback_meals))
        print("Content-based:", len(content_meals))
        print("Collaborative:", len(collaborative_meals))

        # enriched_meals = list({
        #     str(m["_id"]): m
        #     for m in all_meals + content_meals + collaborative_meals
        # }.values())
        logger.info("Logging recommendations: %s", user_id)
        logger.info("Total enriched meals: %s", len(enriched_meals))
        
        # === Ghi lại top-30 món gợi ý để đánh giá precision ===
        try:
            print("Verified user_id:", user_id)
            # for m in enriched_meals[:30]:
            #     print("Meal:", m.get("title"), m.get("_id"))
            # db.recommendation_logs.insert_one({
            #     "user_id": user_id,
            #     "recommended_meals": [str(m["_id"]) for m in enriched_meals[:30]],
            #     "timestamp": datetime.utcnow()
            # })
            top_k_meals = enriched_meals[:30]
            for m in top_k_meals:
                print("Meal:", m.get("title"), m.get("_id"), "Score:", round(m["score"], 4))
            db.recommendation_logs.insert_one({
                "user_id": user_id,
                "recommended_meals": [str(m["_id"]) for m in top_k_meals],
                "timestamp": datetime.utcnow(),
                "used_fallback_collaborative": True if not collaborative_meals_raw else False,
                "cluster_label": cluster_label,
                "collaborative_source_user_ids": similar_user_ids,
            })

        except Exception as e:
            print("Insert log failed:", e)



    # ==== Chức năng lựa chọn món theo ngân sách và calo ====
    def is_valid_energy(val, target):
        return target * 0.9 <= val <= target * 1.1

    def score_meal(meal, target):
        noise = random.uniform(-5, 5)
        return abs(meal["energy"] - target) + 0.3 * meal["price"] + noise

    def select_random_top_n(sorted_list, top_n, budget_left):
        top = [m for m in sorted_list[:top_n] if m["price"] <= budget_left]
        return random.choice(top) if top else None

    def sort_meals_by_score(meals, target):
        return sorted(meals, key=lambda m: score_meal(m, target))

    def pick_main_and_snack(meal_time, meal_calo_target, budget_left, enriched_meals, banned_ids, used_ids):
        main_options = [
            m for m in enriched_meals if m["type"] == "main"
            and m["_id"] not in banned_ids
            and m["_id"] not in used_ids
        ]
        snack_options = [
            m for m in enriched_meals if m["type"] == "snack"
            and m["_id"] not in banned_ids
            and m["_id"] not in used_ids
        ]

        best_combo = None
        valid_combos = []
        min_score = float("inf")

        for main in main_options:
            for snack in snack_options:
                total_energy = main["energy"] + snack["energy"]
                total_price = main["price"] + snack["price"]
                if total_price <= budget_left and is_valid_energy(total_energy, meal_calo_target):
                    score = score_meal(main, meal_calo_target * 0.7) + score_meal(snack, meal_calo_target * 0.3)
                    valid_combos.append((score, (main, snack)))
        valid_combos.sort(key=lambda x: x[0])
        top_combos = valid_combos[:15]
        if top_combos:
            best_combo = random.choice(top_combos)[1]

        # Nếu không tìm được combo hợp lệ thì thử chỉ lấy món chính
        if not best_combo:
            sorted_main = sort_meals_by_score(main_options, meal_calo_target)
            main = select_random_top_n(sorted_main, top_n=30, budget_left=budget_left)
            if main and is_valid_energy(main["energy"], meal_calo_target):
                return main, None

        return best_combo if best_combo else (None, None)


    # ======== Build Suggestions =========
    suggestions = []

    if constraint_type == "daily":
        recent_meal_history = []
        for _ in range(num_days):
            daily_plan = {}
            daily_cost = 0
            daily_used_ids = set()
            banned_ids = set()
            for recent_day in recent_meal_history[-4:]:
                banned_ids.update(recent_day)

            for meal_time in meal_times:
                meal_calo_target = calories * calorie_distribution[meal_time]
                main, snack = pick_main_and_snack(
                    meal_time, meal_calo_target, budget - daily_cost,
                    enriched_meals, banned_ids, daily_used_ids
                )

                if not main:
                    return jsonify({"error": f"Không tìm được món phù hợp cho bữa {meal_time}"}), 400

                daily_cost += main["price"]
                if snack:
                    daily_cost += snack["price"]
                    daily_used_ids.add(snack["_id"])

                daily_used_ids.add(main["_id"])

                daily_plan[meal_time] = {
                    "main": meal_to_dict(main, original_calories=main["energy"], original_cost=main["price"]),
                    "snack": meal_to_dict(snack, original_calories=snack["energy"], original_cost=snack["price"]) if snack else None
                }

            suggestions.append(daily_plan)
            recent_meal_history.append(daily_used_ids)

    else:  # constraint_type == "total"
        max_attempts = 100
        for _ in range(max_attempts):
            temp_suggestions = []
            total_cost = 0
            valid_plan = True
            recent_meal_history = []

            for _ in range(num_days):
                daily_plan = {}
                daily_used_ids = set()
                banned_ids = set()
                for recent_day in recent_meal_history[-4:]:
                    banned_ids.update(recent_day)

                for meal_time in meal_times:
                    meal_calo_target = calories * calorie_distribution[meal_time]
                    main, snack = pick_main_and_snack(
                        meal_time, meal_calo_target, budget - total_cost,
                        enriched_meals, banned_ids, daily_used_ids
                    )

                    if not main:
                        valid_plan = False
                        break

                    daily_used_ids.add(main["_id"])
                    total_cost += main["price"]

                    if snack:
                        daily_used_ids.add(snack["_id"])
                        total_cost += snack["price"]

                    daily_plan[meal_time] = {
                        "main": meal_to_dict(main, original_calories=main["energy"], original_cost=main["price"]),
                        "snack": meal_to_dict(snack, original_calories=snack["energy"], original_cost=snack["price"]) if snack else None
                    }

                if not valid_plan or len(daily_plan) < len(meal_times):
                    break

                temp_suggestions.append(daily_plan)
                recent_meal_history.append(daily_used_ids)

            if valid_plan and len(temp_suggestions) == num_days and total_cost <= budget:
                suggestions = temp_suggestions
                break

        if not suggestions:
            return jsonify({"error": "Không thể tạo đủ 3 bữa mỗi ngày trong giới hạn ngân sách"}), 400

    return jsonify(suggestions), 200






@meals_bp.route("/similar/<meal_id>", methods=["GET"])
def get_similar_meals(meal_id):
    allergens = request.args.getlist("allergens")
    print("Allergens filter:", allergens)
    max_cal = request.args.get("calories", type=float)
    max_price = request.args.get("price", type=float)
    similar_meals = suggest_similar_meals(meal_id, allergens=allergens, max_cal=max_cal, max_price=max_price)  # logic content-based filtering
    return jsonify(similar_meals)


# @meals_bp.route('/suggest_similar/<meal_id>', methods=['GET'])
# def suggest_similar(meal_id):
#     try:
#         similar_meals = suggest_similar_meals(meal_id)
#         return jsonify(similar_meals)
#     except Exception as e:
#         print(f"Error in suggest_similar: {e}")
#         return jsonify({"success": False, "error": str(e)}), 500


@meals_bp.route("/toggle-snack", methods=["POST"])
def toggle_snack():
    data = request.get_json()
    current_main = data.get("currentMain")
    preferences = data.get("preferences", [])
    allergens = data.get("allergens", [])
    print("preferences", preferences)
    print("allergens", allergens)


    if not current_main:
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    result = toggle_snack_logic(current_main, preferences, allergens)

    return jsonify(result)


# @meals_bp.route("/revert-main-only", methods=["POST"])
# def revert_main_only():
#     data = request.get_json()
#     current_main = data.get("currentMain")
#     preferences = data.get("preferences", [])
#     allergens = data.get("allergens", [])

#     if not current_main:
#         return jsonify({"error": "Thiếu dữ liệu"}), 400

#     result = revert_main_only_logic(current_main, preferences, allergens)
#     return jsonify(result)


@meals_bp.route("/search", methods=["GET"])
def search_meals():
    keyword = request.args.get("q", "").strip()
    min_cal = request.args.get("min_cal", type=float)
    max_cal = request.args.get("max_cal", type=float)
    max_price = request.args.get("max_price", type=float)
    meal_type = request.args.get("type")

    if not keyword:
        return jsonify([])

    db = current_app.db

    query = {
        "title": {"$regex": keyword, "$options": "i"}
    }

    # Bổ sung lọc nếu có input
    if min_cal is not None and max_cal is not None:
        query["energy"] = {"$gte": min_cal, "$lte": max_cal}
    if max_price is not None:
        query["price"] = {"$lte": max_price}
    if meal_type in ["main", "snack"]:
        query["type"] = meal_type

    print("Final MongoDB query:", query)

    results = list(db.meals.find(
        query,
        {
            "title": 1, "type": 1, "energy": 1, "price": 1,
            "tags": 1, "ingredients": 1, "main_image": 1, "steps": 1
        }
    ).limit(20))  # Giới hạn 20 món

    def meal_to_brief(m):
        return {
            "id": str(m["_id"]),
            "name": m["title"],
            "type": m.get("type"),
            "calories": m.get("energy"),
            "price": m.get("price"),
            "tags": m.get("tags", []),
            "ingredients": m.get("ingredients", []),
            "image": m.get("main_image", ""),
            "steps": m.get("steps", [])
        }

    return jsonify([meal_to_brief(m) for m in results])


# @meals_bp.route("/search", methods=["GET"])
# def search_meals():
#     keyword = request.args.get("q", "").strip()
#     if not keyword:
#         return jsonify([])

#     db = current_app.db
#     results = list(db.meals.find(
#         {"title": {"$regex": keyword, "$options": "i"}},
#         {"title": 1, "type": 1, "energy": 1, "price": 1, "tags": 1, "ingredients": 1, "main_image": 1, "steps": 1}
#     ).limit(20))  # Giới hạn 20 món

#     # Chuyển về dạng JSON an toàn
#     def meal_to_brief(m):
#         return {
#             "id": str(m["_id"]),
#             "name": m["title"],
#             "type": m.get("type"),
#             "calories": m.get("energy"),
#             "price": m.get("price"),
#             "tags": m.get("tags", []),
#             "ingredients": m.get("ingredients", []),
#             "image": m.get("main_image", ""),
#             "steps": m.get("steps", [])
#         }

#     return jsonify([meal_to_brief(m) for m in results])

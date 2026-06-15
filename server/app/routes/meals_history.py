from flask import Blueprint, request, jsonify, current_app
from app.models.meal_history import MealHistory
from bson import ObjectId
from datetime import datetime
from dateutil.parser import parse as parse_date
from app.utils.auth_decorator import login_required

meals_history_bp = Blueprint("meals_history", __name__, url_prefix="/api/meals_history")

@meals_history_bp.route("/save", methods=["POST"])
@login_required
def save_meal_history(current_user):
    data = request.json
    raw_plan = data.get("plan")
    date_input = data.get("date")
    if date_input:
        try:
            date = parse_date(date_input)
        except Exception:
            return jsonify({"error": "Sai định dạng ngày"}), 400
    else:
        date = datetime.utcnow()

    if not raw_plan or not isinstance(raw_plan, list):
        return jsonify({"error": "Thiếu hoặc sai định dạng thực đơn!"}), 400

    # def simplify_meal_section(section):
    #     return {
    #         key: {"id": value.get("id")}
    #         for key, value in section.items()
    #         if isinstance(value, dict) and "id" in value
    #     }

    def simplify_meal_section(section):
        return {
            "main": {"id": section["main"]["id"]} if section.get("main") and "id" in section["main"] else None,
            "snack": {"id": section["snack"]["id"]} if section.get("snack") and "id" in section["snack"] else None
        }

    simplified_plan = []
    for day in raw_plan:
        if not isinstance(day, dict):
            continue
        simplified_day = {}
        for meal_time, meal_section in day.items():  # Sáng, Trưa, Tối
            if isinstance(meal_section, dict):
                simplified_day[meal_time] = simplify_meal_section(meal_section)
        simplified_plan.append(simplified_day)

    history = MealHistory({
        "user_id": current_user["_id"],
        "date": date,
        "plan": simplified_plan
    })

    inserted = current_app.db.meal_histories.insert_one(history.to_dict())
    return jsonify({"message": "Lưu thực đơn thành công", "id": str(inserted.inserted_id)}), 200

# @meals_history_bp.route("/list", methods=["GET"])
# @login_required
# def get_meal_history(current_user):
#     user_id = str(current_user["_id"])
#     histories = current_app.db.meal_histories.find({"user_id": user_id}).sort("date", -1)

#     result = []
#     for h in histories:
#         item = MealHistory(h).to_dict()
#         item["_id"] = str(h["_id"])
#         result.append(item)

#     return jsonify(result), 200
@meals_history_bp.route("/list", methods=["GET"])
@login_required
def get_meal_history(current_user):
    user_id = str(current_user["_id"])

    # 1. Lấy danh sách meal history của user
    histories_cursor = current_app.db.meal_histories.find({"user_id": user_id}).sort("date", -1)
    histories = list(histories_cursor)

    # 2. Thu thập tất cả meal IDs cần truy vấn
    meal_ids = set()
    for history in histories:
        for day in history.get("plan", []):  # từng ngày
            for time in ["Sáng", "Trưa", "Tối"]:
                meal_time = day.get(time, {})
                for course in ["main", "snack"]:
                    meal_entry = meal_time.get(course)
                    if meal_entry and "id" in meal_entry:
                        try:
                            meal_ids.add(ObjectId(meal_entry["id"]))
                        except Exception:
                            continue

    # 3. Truy vấn meals collection một lần duy nhất
    meals_cursor = current_app.db.meals.find({ "_id": { "$in": list(meal_ids) } })
    meal_dict = {
        str(meal["_id"]): {
            "id": str(meal["_id"]),
            "name": meal["title"],
            "calories": meal["energy"],
            "price": meal["price"],
            "tags": meal["tags"],
            "ingredients": meal.get("ingredients", []),
            "image": meal.get("main_image", ""),
            "steps": meal.get("steps", [])
        }
        for meal in meals_cursor
    }

    # 4. Gộp dữ liệu món ăn vào lịch sử
    result = []
    for history in histories:
        new_plan = []
        for day in history.get("plan", []):  # từng ngày
            new_day = {}
            for time in ["Sáng", "Trưa", "Tối"]:
                meal_time = day.get(time, {})
                new_meal_time = {}
                for course in ["main", "snack"]:
                    entry = meal_time.get(course)
                    if entry and "id" in entry:
                        detailed = meal_dict.get(entry["id"])
                        new_meal_time[course] = detailed if detailed else None
                    else:
                        new_meal_time[course] = None
                new_day[time] = new_meal_time
            new_plan.append(new_day)

        result.append({
            "_id": str(history["_id"]),
            "date": history.get("date"),
            "plan": new_plan
        })

    return jsonify(result), 200

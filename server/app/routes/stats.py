from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from bson import ObjectId
from app.utils.auth_decorator import admin_required
import pytz
import traceback

stats_bp = Blueprint("stats", __name__, url_prefix="/api/stats")

def convert_objectid(obj):
    if isinstance(obj, list):
        return [convert_objectid(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj

def parse_vietnam_date(date_str):
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    if dt.tzinfo is None:
        return tz.localize(dt)
    return dt.astimezone(tz)


@stats_bp.route("/most-selected", methods=["GET"])
@admin_required
def most_selected(current_user):
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        meal_times_str = request.args.get("meal_times", "")
        meal_times = [m for m in meal_times_str.split(",") if m]

        if not start_date or not end_date or not meal_times:
            return jsonify({"error": "Missing parameters"}), 400

        start_dt = parse_vietnam_date(start_date).astimezone(pytz.utc)
        end_dt = (parse_vietnam_date(end_date) + timedelta(days=1)).astimezone(pytz.utc)

        pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": start_dt,
                        "$lt": end_dt
                    }
                }
            },
            { "$unwind": "$plan" },
            {
                "$project": {
                    "meals": {
                        "$concatArrays": [
                            [] if "breakfast" not in meal_times else [
                                { "id": "$plan.Sáng.main.id" },
                                { "id": "$plan.Sáng.snack.id" }
                            ],
                            [] if "lunch" not in meal_times else [
                                { "id": "$plan.Trưa.main.id" },
                                { "id": "$plan.Trưa.snack.id" }
                            ],
                            [] if "dinner" not in meal_times else [
                                { "id": "$plan.Tối.main.id" },
                                { "id": "$plan.Tối.snack.id" }
                            ]
                        ]
                    }
                }
            },
            { "$unwind": "$meals" },
            { "$match": { "meals.id": { "$ne": None } } },
            {
                "$group": {
                    "_id": "$meals.id",
                    "count": { "$sum": 1 }
                }
            },
            {
                "$addFields": {
                    "mealObjectId": { "$toObjectId": "$_id" }
                }
            },
            {
                "$lookup": {
                    "from": "meals",
                    "localField": "mealObjectId",
                    "foreignField": "_id",
                    "as": "meal"
                }
            },
            { "$unwind": "$meal" },
            {
                "$project": {
                    "title": "$meal.title",
                    "count": 1
                }
            },
            { "$sort": { "count": -1 } }
        ]

        stats = list(current_app.db.meal_histories.aggregate(pipeline))
        stats = convert_objectid(stats)

        # Trả về top 5 nhiều nhất và ít nhất
        top20 = stats[:20]
        bottom20 = stats[-20:] if len(stats) > 40 else []

        return jsonify({ "top20": top20, "bottom20": bottom20 })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500


@stats_bp.route("/trend", methods=["GET"])
@admin_required
def meal_trend(current_user):
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        meal_times_str = request.args.get("meal_times", "")
        meal_times = [m for m in meal_times_str.split(",") if m]
        titles_str = request.args.get("titles", "")
        titles = [t.strip() for t in titles_str.split(",") if t.strip()]
        if not start_date or not end_date or not meal_times:
            return jsonify({"error": "Missing parameters"}), 400

        start_dt = parse_vietnam_date(start_date).astimezone(pytz.utc)
        end_dt = (parse_vietnam_date(end_date) + timedelta(days=1)).astimezone(pytz.utc)
        print("Start:", start_date, "End:", end_date)
        print("Titles:", titles)
        print("Meal times:", meal_times)

        pipeline = [
            
            {
                "$match": {
                    "date": {
                        "$gte": start_dt,
                        "$lt": end_dt
                    }
                }
            },
            { "$unwind": "$plan" },
            {
                "$project": {
                    "date": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$date",
                            "timezone": "Asia/Ho_Chi_Minh"
                        }
                    },
                    "meals": {
                        "$concatArrays": [
                            [] if "breakfast" not in meal_times else [
                                { "id": { "$ifNull": ["$plan.Sáng.main.id", None] } },
                                { "id": { "$ifNull": ["$plan.Sáng.snack.id", None] } }
                            ],
                            [] if "lunch" not in meal_times else [
                                { "id": { "$ifNull": ["$plan.Trưa.main.id", None] } },
                                { "id": { "$ifNull": ["$plan.Trưa.snack.id", None] } }
                            ],
                            [] if "dinner" not in meal_times else [
                                { "id": { "$ifNull": ["$plan.Tối.main.id", None] } },
                                { "id": { "$ifNull": ["$plan.Tối.snack.id", None] } }
                            ]
                        ]
                    }
                }
            },
            { "$unwind": "$meals" },
            { "$match": { "meals.id": { "$ne": None } } },
            {
                "$group": {
                    "_id": {
                        "mealId": "$meals.id",
                        "date": "$date"
                    },
                    "count": { "$sum": 1 }
                }
            },
            {
                "$addFields": {
                    "mealObjectId": { "$toObjectId": "$_id.mealId" },
                    "date": "$_id.date"
                }
            },
            {
                "$lookup": {
                    "from": "meals",
                    "localField": "mealObjectId",
                    "foreignField": "_id",
                    "as": "meal"
                }
            },
            { "$unwind": "$meal" },
            *([{
                "$match": {
                    "meal.title": { "$in": titles }
                }
            }] if titles else []),
            {
                "$project": {
                    "date": 1,
                    "count": 1,
                    "title": "$meal.title"
                }
            },
            { "$sort": { "date": 1 } }
        ]

        trend_data = list(current_app.db.meal_histories.aggregate(pipeline))
        
        print("Result trend data:", trend_data)

        return jsonify(convert_objectid(trend_data))

    except Exception as e:
        print("Lỗi khi xử lý /trend:", traceback.format_exc())
        return jsonify({ "error": str(e) }), 500
        


@stats_bp.route("/trend/meals", methods=["GET"])
@admin_required
def get_trend_meals(current_user):
    try:
        pipeline = [
            { "$unwind": "$plan" },
            {
                "$project": {
                    "meals": {
                        "$concatArrays": [
                            [ "$plan.Sáng.main.id", "$plan.Sáng.snack.id",
                              "$plan.Trưa.main.id", "$plan.Trưa.snack.id",
                              "$plan.Tối.main.id", "$plan.Tối.snack.id" ]
                        ]
                    }
                }
            },
            { "$unwind": "$meals" },
            { "$match": { "meals": { "$ne": None } } },
            {
                "$group": {
                    "_id": "$meals"
                }
            },
            {
                "$addFields": {
                    "mealObjectId": { "$toObjectId": "$_id" }
                }
            },
            {
                "$lookup": {
                    "from": "meals",
                    "localField": "mealObjectId",
                    "foreignField": "_id",
                    "as": "meal"
                }
            },
            { "$unwind": "$meal" },
            {
                "$project": {
                    "_id": 0,
                    "title": "$meal.title",
                    "id": "$meal._id"
                }
            },
            { "$sort": { "title": 1 } }
        ]

        meals = list(current_app.db.meal_histories.aggregate(pipeline))
        return jsonify(convert_objectid(meals))
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

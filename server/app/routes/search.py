from flask import Blueprint, request, jsonify, current_app
import os, re, json
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from io import BytesIO
from bson import ObjectId
from pymongo import TEXT
import tempfile

load_dotenv()

search_bp = Blueprint("search_bp", __name__, url_prefix="/api/search")

# Cấu hình Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# Prompt chuẩn
PROMPT = """Nhận diện tất cả nguyên liệu có thể nhìn thấy trong món ăn và trả về mảng dưới dạng JSON gồm tên nguyên liệu bằng tiếng Việt với cấu trúc ["Nguyên liệu 1", "Nguyên liệu 2"]. Chỉ liệt kê nguyên liệu, không mô tả thêm."""

@search_bp.route("/image-search", methods=["POST"])
def image_search():
    if "image" not in request.files:
        return jsonify({"error": "Thiếu ảnh món ăn"}), 400

    image_file = request.files["image"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        image_path = temp.name
        image_file.save(image_path)

    try:
        image = Image.open(image_path)
        response = model.generate_content([PROMPT, image])
        text = response.text

        match = re.search(r"\[.*\]", text, re.DOTALL)
        if not match:
            return jsonify({"error": "Không tìm thấy nguyên liệu trong ảnh"}), 400

        ingredient_names = [i.lower().strip() for i in json.loads(match.group(0))]

        if not ingredient_names:
            return jsonify({"error": "Không nhận diện được nguyên liệu"}), 200


        db = current_app.db
        pipeline = [
            {
                "$addFields": {
                    "matched_ingredients": {
                        "$size": {
                            "$setIntersection": [
                                ingredient_names, 
                                {
                                    "$map": {
                                        "input": "$ingredients",
                                        "as": "ing",
                                        "in": { "$toLower": "$$ing.name" }
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            {"$match": {"matched_ingredients": {"$gt": 0}}},
            {"$sort": {"matched_ingredients": -1}},
            {"$limit": 10}
        ]
        matched_meals = list(db.meals.aggregate(pipeline))


        for meal in matched_meals:
            meal["_id"] = str(meal["_id"])

        return jsonify({
            "ingredients": ingredient_names,
            "meals": matched_meals
        }), 200

    except Exception as e:
        print("Lỗi phân tích ảnh:", e)
        return jsonify({"error": "Lỗi xử lý ảnh hoặc kết nối Gemini"}), 500

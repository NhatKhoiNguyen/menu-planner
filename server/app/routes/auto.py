from flask import Blueprint, request, jsonify, current_app
from app.utils.auth_decorator import login_required
from bson import ObjectId
from dotenv import load_dotenv
import google.generativeai as genai
import os
import json
import re

auto_bp = Blueprint("auto", __name__, url_prefix="/api/auto")

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")


def gemini_call(prompt: str) -> str:
    response = model.generate_content(prompt)
    text = response.text.strip()
    match = re.search(r'\[.*?\]', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

@auto_bp.route("/energy", methods=["POST"])
@login_required
def auto_energy(current_user):
    data = request.json
    ingredients = data.get("ingredients", [])
    title = data.get("title", "")
    if not ingredients or not isinstance(ingredients, list):
        return jsonify({"error": "Thiếu hoặc sai định dạng nguyên liệu"}), 400

    formatted = "\n".join(
        f"- {i.get('name', '')}: {i.get('amount', '')}" for i in ingredients if i.get("name") and i.get("amount")
    )

    if not formatted.strip():
        return jsonify({"error": "Chưa có nguyên liệu hợp lệ"}), 400

    prompt = f"""Tính tổng lượng calories (kcal) cho món ăn từ danh sách nguyên liệu sau:
{formatted}

Chỉ trả lời một số duy nhất, không kèm đơn vị hoặc giải thích."""

    try:
        answer = gemini_call(prompt)
        match = re.search(r"\d+(?:[\.,]\d+)?", answer)
        if match:
            value = match.group(0).replace(",", ".")
            return jsonify({"energy": round(float(value), 2)})
        else:
            return jsonify({"error": "Không đọc được giá trị calo"}), 500
            
    except Exception as e:
        print("Gemini error:", str(e))
        return jsonify({"error": "Không thể ước tính calories"}), 500


@auto_bp.route("/price", methods=["POST"])
@login_required
def auto_price(current_user):
    data = request.json
    ingredients = data.get("ingredients", [])
    if not ingredients or not isinstance(ingredients, list):
        return jsonify({"error": "Thiếu hoặc sai định dạng nguyên liệu"}), 400

    formatted = "\n".join(
        f"- {i.get('name', '')}: {i.get('amount', '')}" for i in ingredients if i.get("name") and i.get("amount")
    )

    if not formatted.strip():
        return jsonify({"error": "Chưa có nguyên liệu hợp lệ"}), 400

    prompt = f"""Tính giá tiền ước lượng (đơn vị VNĐ) dựa vào thị trường thực phẩm Việt Nam gần đây nhất cho món ăn từ danh sách nguyên liệu sau:
{formatted}

Chỉ trả lời bằng một số duy nhất, không kèm đơn vị hoặc giải thích."""

    try:
        answer = gemini_call(prompt)
        match = re.search(r"\d+(?:[\.,]\d+)?", answer)
        if match:
            value = match.group(0).replace(",", ".")
            return jsonify({"price": round(float(value))})
        else:
            return jsonify({"error": "Không đọc được giá trị chi phí"}), 500
    except Exception as e:
        print("Gemini error:", str(e))
        return jsonify({"error": "Không thể ước tính giá"}), 500


@auto_bp.route("/tags", methods=["POST"])
@login_required
def auto_tags(current_user):
    data = request.json
    ingredients = data.get("ingredients", [])
    title = data.get("title", "")
    ALLOWED_TAGS = [
        "Món Á", "Món Âu", "Kết hợp Á - Âu", "Món chay",
        "Ít dầu mỡ", "Không gluten", "Không lactose"
    ]
    if not ingredients or not isinstance(ingredients, list):
        return jsonify({"error": "Thiếu hoặc sai định dạng nguyên liệu"}), 400

    formatted = "\n".join(
        f"- {i.get('name', '')}" for i in ingredients if i.get("name")
    )

    if not formatted.strip():
        return jsonify({"error": "Chưa có nguyên liệu hợp lệ"}), 400

    prompt = f"""Bạn là một chuyên gia dinh dưỡng và đầu bếp chuyên nghiệp. Hãy phân tích món ăn sau để xác định:
Các tags phù hợp (chọn từ danh sách cho trước).
Dữ liệu món ăn:
- Tên món: {title}
- Nguyên liệu: {formatted}

⚠️ Trả về JSON **thô** (không bao quanh bởi dấu ``` hoặc mô tả nào khác) theo đúng mẫu sau:
{{
  ["Món Á", "Món Âu", "Kết hợp Á - Âu", "Món chay", "Ít dầu mỡ", "Không gluten", "Không lactose"]
}}

Chỉ liệt kê các tags phù hợp với món ăn. Nếu không có, để mảng rỗng."""

    try:
        answer = gemini_call(prompt)
        print("Gemini raw answer (tags):", repr(answer))
        if not answer.strip():
            raise ValueError("Không có phản hồi từ Gemini")
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", answer.strip(), flags=re.IGNORECASE)
        tags = json.loads(cleaned)

        if isinstance(tags, str):
            tags = json.loads(tags)

        if not isinstance(tags, list):
            raise ValueError("Tags trả về không phải mảng")

        filtered = [tag for tag in tags if tag in ALLOWED_TAGS]
        return jsonify({"tags": filtered})
    except Exception as e:
        print("Gemini tag error:", str(e))
        return jsonify({"error": "Không thể gợi ý thể loại món ăn"}), 500


@auto_bp.route("/allergens", methods=["POST"])
@login_required
def auto_allergens(current_user):
    data = request.get_json()
    ingredients = data.get("ingredients", [])
    title = data.get("title", "")

    ALLERGENS = ["Trứng", "Hải sản", "Sữa", "Đậu phộng", "Đậu nành", "Lúa mì"]

    if not ingredients or not isinstance(ingredients, list):
        return jsonify({"error": "Thiếu hoặc sai định dạng nguyên liệu"}), 400

    formatted = "\n".join(
        f"- {i.get('name', '')}" for i in ingredients if i.get("name")
    )

    if not formatted.strip():
        return jsonify({"error": "Chưa có nguyên liệu hợp lệ"}), 400

    prompt = f"""Bạn là một chuyên gia dinh dưỡng và đầu bếp chuyên nghiệp. Hãy phân tích món ăn sau để xác định:
Các dị ứng tiềm ẩn (chọn từ danh sách cho trước).
Dữ liệu món ăn:
- Tên món: {title}
- Nguyên liệu: {formatted}

⚠️ Trả về JSON **thô** (không bao quanh bởi dấu ``` hoặc mô tả nào khác) theo đúng mẫu sau:
{{
  ["Trứng", "Hải sản", "Sữa", "Đậu phộng", "Đậu nành", "Lúa mì"]
}}

Chỉ liệt kê các allergens phù hợp với món ăn. Nếu không có, để mảng rỗng."""

    try:
        answer = gemini_call(prompt)
        print("Gemini raw answer (allergens):", repr(answer))

        if not answer.strip():
            raise ValueError("Không có phản hồi từ Gemini")

        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", answer.strip(), flags=re.IGNORECASE)

        allergens = json.loads(cleaned)

        # Nếu Gemini trả chuỗi JSON dạng string
        if isinstance(allergens, str):
            allergens = json.loads(allergens)

        if not isinstance(allergens, list):
            raise ValueError("Kết quả không hợp lệ")

        filtered = [a for a in allergens if a in ALLERGENS]
        return jsonify({"allergens": filtered})
    except Exception as e:
        print("Gemini allergen error:", str(e))
        return jsonify({"error": "Không thể trích xuất dị ứng"}), 500
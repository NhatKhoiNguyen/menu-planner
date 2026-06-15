import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key từ file .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Cấu hình tốc độ gọi API (để không vượt quá giới hạn 15 requests/phút)
REQUESTS_PER_MINUTE = 9
SECONDS_BETWEEN_REQUESTS = 8

model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

def format_ingredients(ingredients):
    return "\n".join([f"- {item['name']}: {item['amount']}" for item in ingredients])

def estimate_calories(ingredients, servings):
    prompt = f"""
Tôi có danh sách nguyên liệu và định lượng cho {servings} khẩu phần ăn như sau:

{format_ingredients(ingredients)}

Hãy ước tính tổng lượng calo (kcal) cho toàn bộ món ăn. Chỉ trả về một con số (ví dụ: 325). Không cần giải thích thêm.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Lỗi khi gọi Gemini API:", e)
        return "Lỗi"

def process_meals(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        meals = json.load(f)

    processed = 0
    for i, meal in enumerate(meals):
        if "energy" in meal and meal["energy"] != "Lỗi":
            continue  # Bỏ qua món đã xử lý

        print(f"🔄 ({i + 1}/{len(meals)}) Đang xử lý: {meal['title']}")
        ingredients = meal.get("ingredients", [])
        servings = meal.get("servings", "1")
        meal["energy"] = estimate_calories(ingredients, servings)
        processed += 1

        # Lưu tạm sau mỗi lần để tránh mất dữ liệu
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(meals, f, ensure_ascii=False, indent=2)

        # Delay để không vượt quá giới hạn RPM
        if processed % REQUESTS_PER_MINUTE == 0:
            print("⏳ Nghỉ 60 giây để tránh vượt giới hạn 15 requests/phút...")
            time.sleep(60)
        else:
            time.sleep(SECONDS_BETWEEN_REQUESTS)

    print(f"✅ Hoàn tất {processed} món. Kết quả lưu vào: {output_file}")


input_path = "single_meals1.json"  # File chứa danh sách món ăn theo cấu trúc bạn gửi
output_path = "meals_with_calories1total.json"  # File xuất kết quả
process_meals(input_path, output_path)

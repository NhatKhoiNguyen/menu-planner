import json
import os
import time
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Constants for Gemini rate limiting
REQUESTS_PER_MINUTE = 5
SECONDS_BETWEEN_REQUESTS = 40 
last_request_time = 0

# Load environment and Gemini model
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

current_dir = os.path.dirname(os.path.abspath(__file__))
crawler_dir = os.path.join(current_dir, "../app/crawler")

# Load data
with open(os.path.join(crawler_dir, "meals_tagged17.json"), "r", encoding="utf-8") as f:
    meals = json.load(f)
# with open("meals_with_prices_total3.json", "r", encoding="utf-8") as f:
#     meals = json.load(f)


def estimate_meal_price(meal_title, ingredients):
    global last_request_time
    elapsed = time.time() - last_request_time
    if elapsed < SECONDS_BETWEEN_REQUESTS:
        time.sleep(SECONDS_BETWEEN_REQUESTS - elapsed)

    ingredient_lines = "\n".join(f"- {ing['name']}: {ing.get('amount', 'vừa đủ')}" for ing in ingredients)

    prompt = f"""
Tôi có món ăn tên là "{meal_title}" gồm các nguyên liệu sau:

{ingredient_lines}

Hãy ước tính tổng chi phí để mua toàn bộ các nguyên liệu trên tại Việt Nam.
Chỉ trả về duy nhất một con số là tổng giá tiền bằng đồng Việt Nam (viết số, không kèm chữ hay đơn vị).
"""

    try:
        response = gemini_model.generate_content(prompt)
        last_request_time = time.time()
        print(f"🟨 {meal_title}: {response.text.strip()}")
        match = re.search(r"\d[\d,.]*", response.text)
        if match:
            price_str = match.group(0).replace(",", "").replace(".", "")
            return float(price_str)
        return 0
    except Exception as e:
        print(f"🟥 Gemini error ({meal_title}):", e)
        return 0


# Main loop
for meal in meals:
    title = meal.get("title", "Không tên")
    ingredients = meal.get("ingredients", [])
    estimated_price = estimate_meal_price(title, ingredients)
    meal["price"] = round(estimated_price)

# Save output
with open("meals_with_prices_gemini5.json", "w", encoding="utf-8") as f:
    json.dump(meals, f, ensure_ascii=False, indent=2)

print("✅ Done: meals_with_prices_gemini5.json")

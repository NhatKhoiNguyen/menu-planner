import os
import time
import json
from dotenv import load_dotenv
import google.generativeai as genai
from tqdm import tqdm
from collections import deque

# Load biến môi trường
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

# File nguồn & đích
# INPUT_FILE = "batches/meals_batch_15.json"
INPUT_FILE = "meals_with_calories1total.json"
OUTPUT_FILE = "meals_tagged17.jsonl"

MAX_REQUESTS_PER_MIN = 12
TIME_WINDOW = 60
request_times = deque()

# Hàm delay nếu vượt quá số lần cho phép
def wait_if_needed():
    current_time = time.time()
    while request_times and current_time - request_times[0] > TIME_WINDOW:
        request_times.popleft()

    if len(request_times) >= MAX_REQUESTS_PER_MIN:
        sleep_time = TIME_WINDOW - (current_time - request_times[0]) + 1
        print(f"⏳ Đang chờ {sleep_time:.1f}s để tránh vượt quota...")
        time.sleep(sleep_time)
        request_times.popleft()

    request_times.append(time.time())


# Đọc danh sách món cần xử lý
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    all_meals = json.load(f)

# Đọc các món đã xử lý nếu có
processed_titles = set()
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                meal = json.loads(line.strip())
                processed_titles.add(meal["title"])
            except:
                continue

# Hàm phân tích món
def classify_meal(meal):
    ingredients = [ing["name"] for ing in meal.get("ingredients", [])]
    steps = " ".join([step.get("step", "") for step in meal.get("steps", [])])

    prompt = f"""
Bạn là một chuyên gia dinh dưỡng và đầu bếp chuyên nghiệp. Hãy phân tích món ăn sau để xác định:
1. Các tags phù hợp (chọn từ danh sách cho trước),
2. Loại món (main hoặc snack),
3. Các dị ứng tiềm ẩn (chọn từ danh sách cho trước).

Dữ liệu món ăn:
- Tên món: {meal.get("title", "")}
- Nguyên liệu: {ingredients}
- Cách làm: {steps}

⚠️ Trả về JSON **thô** (không bao quanh bởi dấu ``` hoặc mô tả nào khác) theo đúng mẫu sau:
{{
  "tags": ["Món Á", "Món Âu", "Kết hợp Á - Âu", "Món chay", "Ít dầu mỡ", "Không gluten", "Không lactose"],
  "type": "main" hoặc "snack",
  "allergens": ["Trứng", "Hải sản", "Sữa", "Đậu phộng", "Đậu nành", "Lúa mì"]
}}

Chỉ liệt kê các tags và allergens phù hợp với món ăn. Nếu không có, để mảng rỗng.
"""

    try:
        wait_if_needed()
        response = model.generate_content(prompt)
        content = response.text.strip()

        if content.startswith("```"):
            content = content.strip("```json").strip("```").strip()

        result = json.loads(content)
        return result
    except Exception as e:
        print(f"\n❌ Lỗi phân tích món '{meal.get('title', '')}': {e}")
        try:
            print("↪ Nội dung phản hồi từ Gemini:")
            print(content[:300])
        except:
            pass
        return {"tags": [], "type": "main", "allergens": []}

# Xử lý từng món chưa được xử lý
to_process = [m for m in all_meals if m["title"] not in processed_titles]

MAX_REQUESTS_PER_MINUTE = 12
DELAY_BETWEEN_BATCHES = 60  # giây

batch_counter = 0

for i, meal in enumerate(tqdm(to_process, desc="Đang gán tags và dị ứng...")):
    result = classify_meal(meal)
    meal["tags"] = result["tags"]
    meal["type"] = result["type"]
    meal["allergens"] = result["allergens"]

    # Ghi ngay vào file .jsonl
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        json.dump(meal, f, ensure_ascii=False)
        f.write("\n")

    batch_counter += 1
    if batch_counter >= MAX_REQUESTS_PER_MINUTE:
        if i < len(to_process) - 1:
            time.sleep(8.2)
        print("⏳ Đợi 60s để tránh vượt quota...")
        time.sleep(DELAY_BETWEEN_BATCHES)
        batch_counter = 0
    else:
        time.sleep(8)

    # if i < len(to_process) - 1:
    #     time.sleep(5.2)

print("✅ Đã gán xong tags, loại món và dị ứng!")

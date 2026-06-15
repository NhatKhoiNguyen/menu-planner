# import requests

# img = r'C:\Users\TechCare\Pictures\meal planner\cach-lam-khoai-tay-nuong-bo-mon-an-sang-734634530415.jpg'
# api_user_token = 'cf2141eb3787f9ad47d1ad2d9b452a215bddc00d'
# headers = {'Authorization': 'Bearer ' + api_user_token}

# # Gửi ảnh lên segmentation API để lấy imageId
# url = 'https://api.logmeal.com/v2/image/segmentation/complete'
# resp = requests.post(url, files={'image': open(img, 'rb')}, headers=headers)
# image_id = resp.json()['imageId']

# # Gửi imageId để lấy thông tin nguyên liệu
# url = 'https://api.logmeal.com/v2/recipe/ingredients'
# resp = requests.post(url, json={'imageId': image_id}, headers=headers)
# result = resp.json()

# # ✅ Lấy riêng mảng foodName
# food_names = result.get('foodName', [])

# print(food_names)  # In ra danh sách tên món

# import json
# import os
# from dotenv import load_dotenv
# import google.generativeai as genai
# from PIL import Image

# # Constants for Gemini rate limiting
# REQUESTS_PER_MINUTE = 5
# SECONDS_BETWEEN_REQUESTS = 40 
# last_request_time = 0

# # Load environment and Gemini model
# load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# img = Image.open(r'C:\Users\TechCare\Pictures\meal planner\cach-lam-khoai-tay-nuong-bo-mon-an-sang-734634530415.jpg')
# model = genai.GenerativeModel("gemini-2.5-flash")
# prompt = f"""Nhận diện tất cả nguyên liệu có thể nhìn thấy trong món ăn và trả về mảng dưới dạng JSON gồm tên nguyên liệu bằng tiếng Việt với cấu trúc ["Nguyên liệu 1", "Nguyên liệu 2"]. Chỉ liệt kê nguyên liệu, không mô tả thêm."""
# response = model.generate_content([prompt, img])
# print(response.text)

import re
import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Kết nối MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["meal_planner_db"]
meals_collection = db["meals"]

# Nhận diện nguyên liệu từ ảnh
img = Image.open(r'C:\Users\TechCare\Pictures\meal planner\cach-lam-khoai-tay-nuong-bo-mon-an-sang-734634530415.jpg')
model = genai.GenerativeModel("gemini-2.5-flash")

prompt = """
Nhận diện tất cả nguyên liệu có thể nhìn thấy trong món ăn và trả về mảng dưới dạng JSON gồm tên nguyên liệu bằng tiếng Việt với cấu trúc ["Nguyên liệu 1", "Nguyên liệu 2"]. Chỉ liệt kê nguyên liệu, không mô tả thêm.
"""

response = model.generate_content([prompt, img])
print("===== RESPONSE TEXT FROM GEMINI =====")
print(response.text)

match = re.search(r"\[.*\]", response.text, re.DOTALL)
if match:
    try:
        ingredients_list = json.loads(match.group(0))
        print("✅ Ingredients list:", ingredients_list)
    except json.JSONDecodeError:
        print("❌ Không thể parse JSON từ đoạn:", match.group(0))
else:
    print("❌ Không tìm thấy JSON hợp lệ trong phản hồi Gemini.")


print("Nguyên liệu nhận diện:", ingredients_list)

# Tiền xử lý: lower-case để khớp dễ hơn
ingredients_set = set(ing.lower() for ing in ingredients_list)

# Tìm món ăn có ít nhất một nguyên liệu trùng
results = []
for meal in meals_collection.find():
    meal_ingredients = {ing["name"].lower() for ing in meal.get("ingredients", [])}
    matched = ingredients_set & meal_ingredients
    if matched:
        results.append({
            "meal_id": str(meal["_id"]),
            "title": meal.get("title"),
            "matched_ingredients": list(matched),
            "match_count": len(matched),
            "total_ingredients": len(meal_ingredients),
            "score": len(matched) / max(len(meal_ingredients), 1)
        })

# Sắp xếp theo độ khớp cao nhất
results = sorted(results, key=lambda x: x["score"], reverse=True)

# Trả về 10 món ăn khớp nhất
top_matches = results[:10]

# Kết quả cho frontend
print(json.dumps(top_matches, ensure_ascii=False, indent=2))

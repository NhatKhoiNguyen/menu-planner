import json
from pymongo import MongoClient

# Kết nối MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['meal_planner_db']
collection = db['meals']

with open('meals_with_prices_gemini5.json', 'r', encoding='utf-8') as f:
    meals = json.load(f)

for meal in meals:
    meal['servings'] = int(meal['servings'])
    meal['energy'] = int(meal['energy'])
    meal['lastPriceUpdatedDate'] = None

# collection.delete_many({})

# Chèn mới
collection.insert_many(meals)

print(f"✅ Đã chèn {len(meals)} món ăn vào MongoDB.")

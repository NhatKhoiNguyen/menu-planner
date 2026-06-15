from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from unidecode import unidecode
import json

# client = MongoClient("mongodb://localhost:27017")
# db = client["meal_planner_db"]
# meals_collection = db["meals"]

# model = SentenceTransformer("all-MiniLM-L6-v2")

# def meal_to_text(meal):
#     parts = []
#     parts.extend(meal.get("tags", []))
#     parts.extend(meal.get("ingredients", []))
#     parts.append(meal.get("description", ""))
#     parts.append(meal.get("type", ""))
#     return " ".join(parts)

# def update_all_meal_embeddings():
#     meals = list(meals_collection.find({}))
#     for meal in meals:
#         text = meal_to_text(meal)
#         embedding = model.encode(text).tolist()
#         meals_collection.update_one(
#             {"_id": meal["_id"]},
#             {"$set": {"embedding": embedding}}
#         )
#         print(f"✅ Updated: {meal['name']}")


# Khởi tạo model (chỉ nên load 1 lần trong app)
model = SentenceTransformer("all-MiniLM-L6-v2")

STOP_INGREDIENTS = {
    "muối", "đường", "nước", "dầu", "tiêu", "hành", "tỏi", "gừng",
    "ớt", "bột ngọt", "nước mắm", "bột nêm", "bột mì", "bột năng"
}

def normalize_text(text):
    text = unidecode(text)
    text = text.lower()
    return "".join(c for c in text if c.isalnum() or c.isspace())

def get_meal_embedding_ingredients(meal):
    tags = [normalize_text(tag) for tag in meal.get("tags", [])]
    raw_ingredients = [i.get("name", "") for i in meal.get("ingredients", [])]

    ingredients = [
        normalize_text(i)
        for i in raw_ingredients
        if normalize_text(i) not in STOP_INGREDIENTS
    ]
    
    meal_type = normalize_text(meal.get("type", ""))
    title = normalize_text(meal.get("title", ""))

    text = " ".join(
        tags
        + ingredients * 2
        + [meal_type]
        + [title]
    )
    return model.encode(text, convert_to_numpy=True, show_progress_bar=False)

# def get_meal_embedding(meal):
#     try:
#         tags = [normalize_text(tag) for tag in meal.get("tags", []) if tag]
#         raw_ingredients = [i.get("name", "") for i in meal.get("ingredients", []) if i.get("name")]

#         ingredients = [
#             normalize_text(i)
#             for i in raw_ingredients
#             if normalize_text(i) not in STOP_INGREDIENTS
#         ]

#         meal_type = normalize_text(meal.get("type", "") or "")
#         title = normalize_text(meal.get("title", "") or "")

#         text = " ".join(
#             tags
#             + ingredients * 2
#             + [meal_type]
#             + [title]
#         ).strip()

#         # Nếu text rỗng, trả về chuỗi "unknown"
#         return text if text else "unknown"

#     except Exception as e:
#         print("Error in get_meal_embedding:", e)
#         return "unknown"


def get_meal_embedding(meal):
    emb = meal.get("embedding", [])
    if isinstance(emb, str):
        try:
            emb = json.loads(emb)  # chuyển chuỗi -> list
        except json.JSONDecodeError:
            return np.zeros(384).tolist()  # hoặc chiều embedding mặc định
    return emb

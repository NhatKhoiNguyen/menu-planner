# scripts/generate_meal_embeddings.py
import os

from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np
import bson

client = MongoClient(os.getenv("MONGO_URI"))
db = client["meal_planner_db"]
meals = db["meals"]

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_meal_text(meal):
    title = meal.get("title", "")
    tags = " ".join(meal.get("tags", []))
    ingredients = " ".join(i.get("name", "") for i in meal.get("ingredients", []))
    return f"{title} {tags} {ingredients}"

batch = []
for meal in meals.find({"embedding": {"$exists": False}}):
    text = get_meal_text(meal)
    embedding = model.encode(text).tolist()
    batch.append(
        {
            "_id": meal["_id"],
            "embedding": embedding
        }
    )

# Cập nhật vào DB
for item in batch:
    meals.update_one({"_id": item["_id"]}, {"$set": {"embedding": item["embedding"]}})
print("✅ Embedding updated for", len(batch), "meals.")

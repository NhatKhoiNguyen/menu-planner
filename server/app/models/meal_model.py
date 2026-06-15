import os

from pymongo import MongoClient

client = MongoClient(os.getenv("MONGO_URI"))
db = client["meal_planner_db"]
meals_collection = db["meals"]

def get_meals_by_type(meal_type):
    return list(meals_collection.find({"type": meal_type}, {
        "_id": 0,  # loại bỏ ObjectId
        "id": 1,
        "name": 1,
        "calories": 1,
        "price": 1,
        "image": 1
    }))

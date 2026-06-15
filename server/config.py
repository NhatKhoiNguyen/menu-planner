import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "meal_planner_db")

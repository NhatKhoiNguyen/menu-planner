# scripts/cluster_users_by_ingredients.py
from pymongo import MongoClient
from bson import ObjectId
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
import pickle
from collections import defaultdict

def get_user_ingredient_vector(user_meal_ids, meals_collection, all_ingredient_names):
    vector = np.zeros(len(all_ingredient_names))
    name_to_idx = {name: i for i, name in enumerate(all_ingredient_names)}

    for meal in meals_collection.find({"_id": {"$in": list(user_meal_ids)}}):
        for ing in meal.get("ingredients", []):
            name = ing.get("name", "")
            if name in name_to_idx:
                vector[name_to_idx[name]] += 1
    return vector

def extract_meal_ids(plan):
    meal_ids = set()
    for day in plan:
        for meal_time in ["Sáng", "Trưa", "Tối"]:
            meal_info = day.get(meal_time, {})
            for mtype in ["main", "snack"]:
                meal = meal_info.get(mtype)
                if meal and "id" in meal:
                    try:
                        meal_ids.add(ObjectId(meal["id"]))
                    except:
                        pass
    return list(meal_ids)

def main():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["meal_planner_db"]
    meals_collection = db["meals"]
    histories_collection = db["meal_histories"]

    # Danh sách tất cả nguyên liệu
    all_ingredient_names = sorted(
        {ing["name"] for m in meals_collection.find() for ing in m.get("ingredients", [])}
    )

    # Gom tất cả meal_ids theo user_id
    user_to_meal_ids = defaultdict(set)

    for doc in histories_collection.find():
        user_id = doc["user_id"]
        meal_ids = extract_meal_ids(doc["plan"])
        user_to_meal_ids[user_id].update(meal_ids)

    # Tính vector nguyên liệu cho từng người dùng
    user_vectors = []
    user_ids = []

    # Tính vector 1 lần cho mỗi user
    for user_id, meal_ids in user_to_meal_ids.items():
        vec = get_user_ingredient_vector(meal_ids, meals_collection, all_ingredient_names)
        if np.sum(vec) > 0:
            user_vectors.append(vec)
            user_ids.append(user_id)
            

    if not user_vectors:
        print("Không có vector người dùng để clustering.")
        return
    if len(user_vectors) < 3:
        print("Không đủ người dùng để phân cụm (tối thiểu 3).")
        return

    X = normalize(np.array(user_vectors))
    n_clusters = min(max(2, len(user_vectors) // 2), 10)

    kmeans = KMeans(n_clusters=n_clusters, n_init="auto", random_state=42)
    labels = kmeans.fit_predict(X)

    # Gán lại cluster_id vào MongoDB
    for uid, label in zip(user_ids, labels):
        histories_collection.update_many(
            {"user_id": uid},
            {"$set": {"cluster_id": int(label)}}
        )

    # Lưu kết quả vào file (tùy chọn để load nhanh hơn)
    with open("user_clusters.pkl", "wb") as f:
        pickle.dump({
            "user_ids": user_ids,
            "labels": labels.tolist(),
            "ingredient_names": all_ingredient_names
        }, f)

    print(f"✅ Đã gán cluster cho {len(user_ids)} người dùng thành {n_clusters} cụm.")

if __name__ == "__main__":
    main()

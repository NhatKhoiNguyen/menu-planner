from pymongo import MongoClient
from bson import ObjectId
from collections import defaultdict
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
import csv
import itertools
import numpy as np


### Hàm tính toán
def jaccard_distance(set1, set2):
    if not set1 or not set2:
        return 1.0
    return 1 - len(set1 & set2) / len(set1 | set2)

def calculate_diversity(meals):
    titles = [set(m["title"].lower().split()) for m in meals]
    pairs = list(itertools.combinations(titles, 2))
    if not pairs:
        return 0.0
    distances = [jaccard_distance(a, b) for a, b in pairs]
    return round(sum(distances) / len(distances), 4)

def calculate_novelty(top_k, true_ids):
    if not top_k:
        return 0.0
    novel_count = sum(1 for mid in top_k if mid not in true_ids)
    return round(novel_count / len(top_k), 4)

def calculate_serendipity(top_k_ids, true_ids, id_to_score):
    if not top_k_ids:
        return 0.0
    surprise_count = sum(1 for mid in top_k_ids if mid not in true_ids and id_to_score.get(mid, 0) >= 0.9)
    return round(surprise_count / len(top_k_ids), 4)

def calculate_coverage(recommended_all_ids, total_meal_count):
    if not total_meal_count:
        return 0.0
    return round(len(recommended_all_ids) / total_meal_count, 4)

### Kết nối DB
client = MongoClient("mongodb://localhost:27017/")
db = client["meal_planner_db"]

meal_histories = db["meal_histories"]
recommendation_logs = db["recommendation_logs"]
meals = db["meals"]

### Build user ground truth
cutoff_date = datetime.utcnow() - timedelta(days=60)
user_true_meals = defaultdict(set)

for history in meal_histories.find():
    uid = str(history["user_id"])
    for plan in history.get("plan", []):
        if "date" in plan:
            try:
                if datetime.strptime(plan["date"], "%Y-%m-%d") < cutoff_date:
                    continue
            except:
                continue
        for t in ["Sáng", "Trưa", "Tối"]:
            meal = plan.get(t, {})
            for part in ["main", "snack"]:
                mid = meal.get(part, {}).get("id")
                if mid:
                    user_true_meals[uid].add(str(mid))

### Load all meals
all_meal_ids = {str(m["_id"]) for m in meals.find({}, {"_id": 1})}
meal_map = {str(m["_id"]): m for m in meals.find({}, {"_id": 1, "title": 1})}

### Lấy tất cả recommendation logs
logs_by_user = defaultdict(list)

for log in recommendation_logs.find():
    uid = str(log["user_id"])
    ts = log.get("timestamp") or log.get("created_at") or datetime.min
    logs_by_user[uid].append({"log": log, "ts": ts})

### Tách ra log mới nhất và toàn bộ log
latest_logs = {
    uid: max(user_logs, key=lambda x: x["ts"])["log"]
    for uid, user_logs in logs_by_user.items()
}

all_logs = {
    uid: [entry["log"] for entry in user_logs]
    for uid, user_logs in logs_by_user.items()
}


### Đánh giá
def evaluate(logs_dict, eval_type):
    results = []
    recommended_all_ids = set()

    for uid, logs in logs_dict.items():
        true_ids = user_true_meals.get(uid, set())
        if not true_ids:
            continue

        logs_list = logs if isinstance(logs, list) else [logs]

        for log in logs_list:
            rec_ids = [str(mid) for mid in log.get("recommended_meals", [])]
            scores = {str(mid): 1.0 for mid in rec_ids}

            if "recommended_meals_scores" in log:
                scores = {
                    str(mid): float(score)
                    for mid, score in zip(log["recommended_meals"], log["recommended_meals_scores"])
                }

            if not rec_ids:
                continue

            recommended_all_ids.update(rec_ids)

            for k in [5, 10, 30]:
                top_k = rec_ids[:k]
                hits = sum(1 for mid in top_k if mid in true_ids)
                precision = hits / k
                recall = hits / len(true_ids)
                f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
                novelty = calculate_novelty(top_k, true_ids)
                serendipity = calculate_serendipity(top_k, true_ids, scores)

                meal_docs = [meal_map.get(mid) for mid in top_k if mid in meal_map]
                diversity = calculate_diversity(meal_docs) if len(meal_docs) > 1 else ""

                satisfaction_proxy = round(
                    0.4 * precision + 0.3 * novelty + 0.3 * (diversity if isinstance(diversity, float) else 0), 4
                )

                results.append({
                    "user_id": uid,
                    "evaluation_type": eval_type,
                    "k": k,
                    "precision": round(precision, 4),
                    "recall": round(recall, 4),
                    "f1": round(f1, 4),
                    "hits": hits,
                    "true_count": len(true_ids),
                    "novelty": novelty,
                    "diversity": diversity,
                    "serendipity": serendipity,
                    "user_satisfaction_proxy": satisfaction_proxy
                })

    coverage = calculate_coverage(recommended_all_ids, len(all_meal_ids))
    print(f"✅ Coverage ({eval_type}): {coverage*100:.2f}%")
    return results


### Chạy đánh giá
result_latest = evaluate(latest_logs, "latest")
result_all = evaluate(all_logs, "all_logs")

total_results = result_latest + result_all

### Xuất CSV
with open("evaluation_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "user_id", "evaluation_type", "k", "precision", "recall", "f1",
        "hits", "true_count", "novelty", "diversity", "serendipity", "user_satisfaction_proxy"
    ])
    writer.writeheader()
    writer.writerows(total_results)

print("✅ Đã ghi kết quả vào file evaluation_results.csv")



# for history in meal_histories.find():
#     user_id = str(history["user_id"])
#     for plan in history.get("plan", []):
#         for b in ["Sáng", "Trưa", "Tối"]:
#             meal = plan.get(b)
#             if not isinstance(meal, dict):
#                 continue

#             main = meal.get("main")
#             if isinstance(main, dict) and main.get("id"):
#                 user_true_meals[user_id].add(str(main["id"]))

#             snack = meal.get("snack")
#             if isinstance(snack, dict) and snack.get("id"):
#                 user_true_meals[user_id].add(str(snack["id"]))


# # Tính Precision@5
# total_users = 0
# total_hits = 0
# seen_users = set()

# latest_logs = {}

# for log in recommendation_logs.find():
#     user_id = str(log["user_id"])
#     ts = log.get("timestamp") or log.get("created_at") or datetime.min
#     if user_id not in latest_logs or ts > latest_logs[user_id]["ts"]:
#         latest_logs[user_id] = {"log": log, "ts": ts}

# for user_id, entry in latest_logs.items():
#     log = entry["log"]
#     recommended_ids = [str(rid) for rid in log.get("recommended_meals", [])][:30]
#     true_ids = user_true_meals.get(user_id, set())

#     if not true_ids:
#         continue

#     hits = sum(1 for rec_id in recommended_ids if rec_id in true_ids)
#     precision = hits / 30

#     total_hits += precision
#     total_users += 1


# if total_users > 0:
#     avg_precision_at_30 = total_hits / total_users
#     print(f"📊 Precision@30 = {avg_precision_at_30:.4f} ({total_users} users)")
# else:
#     print("⚠️ Không có người dùng đủ dữ liệu để đánh giá.")

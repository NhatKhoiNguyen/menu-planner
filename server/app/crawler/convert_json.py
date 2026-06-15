import json

with open("meals_tagged17.jsonl", "r", encoding="utf-8") as f_in, open("meals_tagged17.json", "w", encoding="utf-8") as f_out:
    meals = [json.loads(line) for line in f_in]
    json.dump(meals, f_out, ensure_ascii=False, indent=2)

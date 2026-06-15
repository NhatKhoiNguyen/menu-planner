# Modified script that adds AI-based ingredient matching using sentence-transformers and cosine similarity.

import json
import re
from difflib import get_close_matches
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load data
with open("single_meals.json", encoding="utf-8") as f:
    meals = json.load(f)
with open("ingredients_energy.json", encoding="utf-8") as f:
    energy_data = json.load(f)
with open("food_weights_converted.json", encoding="utf-8") as f:
    weight_data = json.load(f)

# Danh sách nguyên liệu gia vị
seasonings = ["muối", "đường", "tiêu", "nước mắm", "bột ngọt", "bột nêm", "hạt nêm",
              "dầu ăn", "dầu mè", "sốt", "bột tỏi", "ngò", "ớt", "gừng", "hành", "tỏi"]

# Đơn vị luôn bỏ qua
strictly_ignored_units = ["muỗng canh", "muỗng cà phê"]

def is_seasoning(ingredient_name):
    return any(season in ingredient_name.lower() for season in seasonings)

def normalize(text):
    return re.sub(r"[^a-zA-ZÀ-ỹ0-9 ]", "", text.lower()).strip()

# Load sentence-transformer model for embedding
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Precompute embeddings for energy_data names
energy_names = [entry["Tên"] for entry in energy_data]
normalized_names = [normalize(name) for name in energy_names]
energy_embeddings = model.encode(normalized_names)

def find_energy_ai(ingredient_name, threshold=0.7):
    input_clean = normalize(ingredient_name)
    input_embedding = model.encode([input_clean])
    similarities = cosine_similarity(input_embedding, energy_embeddings)[0]
    best_idx = np.argmax(similarities)
    best_score = similarities[best_idx]
    if best_score >= threshold:
        matched_entry = energy_data[best_idx]
        print(f"🔍 AI matched: '{ingredient_name}' → '{matched_entry['Tên']}' (score: {best_score:.2f})")
        return matched_entry["Năng lượng"]
    return None

def find_energy_combined(ingredient_name):
    name_clean = normalize(ingredient_name)
    candidates = [normalize(entry["Tên"]) for entry in energy_data]
    matches = get_close_matches(name_clean, candidates, n=1, cutoff=0.4)
    if matches:
        matched_name = matches[0]
        for entry in energy_data:
            if normalize(entry["Tên"]) == matched_name:
                return entry["Năng lượng"]
    # Fallback to AI-based matching
    return find_energy_ai(ingredient_name)

def extract_quantity(amount):
    match = re.match(r"(\d+\/\d+|\d+\.\d+|\d+)", amount)
    if match:
        try:
            return eval(match.group(1))
        except:
            return None
    return None

def convert_to_gram(name, amount):
    name_clean = normalize(name)
    amount_lower = amount.lower().replace("trái", "quả").strip()

    if any(unit in amount_lower for unit in strictly_ignored_units):
        return None

    quantity = extract_quantity(amount_lower)
    if quantity is None:
        return None

    if "g" in amount_lower or "gram" in amount_lower:
        return quantity

    if "ml" in amount_lower or "mililít" in amount_lower:
        return quantity

    for entry in weight_data:
        entry_name = normalize(entry["name"])
        entry_unit = entry["unit"].lower().replace("trái", "quả")
        if name_clean.startswith(entry_name) and entry_unit in amount_lower:
            return quantity * entry["weight"]

    if "cái" in amount_lower:
        return None

    return None

def calculate_meal_energy(meal):
    total_kcal = 0
    for ing in meal["ingredients"]:
        name = ing["name"]
        amount = ing["amount"]

        if is_seasoning(name):
            continue

        energy_per_100g = find_energy_combined(name)
        weight_in_gram = convert_to_gram(name, amount)

        print(f"[{name}] - {amount} → {weight_in_gram}g, {energy_per_100g} kcal/100g")

        if energy_per_100g is not None and weight_in_gram is not None:
            kcal = (energy_per_100g * weight_in_gram) / 100
            total_kcal += kcal
        else:
            print(f"⚠️ Không tính được năng lượng cho: {name} - {amount}")

    return round(total_kcal, 1)

# Tính năng lượng cho từng món
for meal in meals:
    meal["energy"] = calculate_meal_energy(meal)

# Ghi ra file
output_path = "single_meals_with_energy.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(meals, f, ensure_ascii=False, indent=2)

print(f"\n✅ Đã tính xong năng lượng và lưu vào {output_path}")

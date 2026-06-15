import json
from underthesea import word_tokenize
from sentence_transformers import SentenceTransformer, util

# Load mô hình embedding
model = SentenceTransformer("distiluse-base-multilingual-cased-v1")

# Danh sách từ khóa theo nhóm
GLUTEN_INGREDIENTS = ["lúa mì", "bột mì", "mì căn", "gluten"]
LACTOSE_INGREDIENTS = ["sữa", "bơ", "phô mai", "kem"]
SEAFOOD_INGREDIENTS = ["tôm", "cua", "ghẹ", "mực", "bạch tuộc", "cá"]
MEAT_INGREDIENTS = ["thịt", "gà", "heo", "bò", "vịt"]
VEGETARIAN_EXCEPTIONS = MEAT_INGREDIENTS + SEAFOOD_INGREDIENTS + ["trứng"]
ASIAN_SPICES = ["nước mắm", "hành", "ngò", "dầu mè", "sa tế", "nước màu"]
EUROPEAN_INGREDIENTS = ["phô mai", "bơ", "tỏi", "húng quế", "parsley", "olive oil", "bánh mì", "cà chua"]
ALLERGENS = ["trứng", "đậu phộng", "sữa", "hải sản", "đậu nành", "lúa mì"]
MAIN_EXAMPLES = ["cơm thịt kho", "mì xào hải sản", "bún bò huế", "canh chua cá", "phở gà", "cơm tấm sườn", "gà nướng mật ong", "bánh xèo", "bún thịt nướng", "cá kho tộ", "cà ri gà", "sườn nướng", "lẩu hải sản", "bò lúc lắc", "cá chiên xù", "salad gà", "salad cá"]
SNACK_EXAMPLES = ["chè đậu xanh", "bánh flan", "sữa chua", "bánh quy", "trái cây", "bánh ngọt", "sinh tố dâu", "pudding", "mousse", "tiramisu", "bánh kem", "bánh mì kẹp thịt", "bánh bao", "salad trộn", "salad rau củ", "sinh tố bơ", "sinh tố chuối"]

# Danh sách gợi ý tag
TAG_KEYWORDS = {
    "Không gluten": GLUTEN_INGREDIENTS,
    "Không lactose": LACTOSE_INGREDIENTS,
    "Hải sản": SEAFOOD_INGREDIENTS,
    "Thịt": MEAT_INGREDIENTS,
    "Chay": VEGETARIAN_EXCEPTIONS,
    "Món Á": ASIAN_SPICES,
    "Món Âu hoặc khác": EUROPEAN_INGREDIENTS,
}

# Tạo embedding cho mỗi nhóm
tag_embeddings = {
    tag: model.encode(keywords, convert_to_tensor=True)
    for tag, keywords in TAG_KEYWORDS.items()
}
allergen_embeddings = model.encode(ALLERGENS, convert_to_tensor=True)

# Phân loại món ăn (main/snack)
# Tạo embedding một lần
main_embeds = model.encode(MAIN_EXAMPLES, convert_to_tensor=True)
snack_embeds = model.encode(SNACK_EXAMPLES, convert_to_tensor=True)

def classify_meal(meal, threshold=0.45):
    meal_text = meal.get("title", "").lower()
    energy = meal.get("energy", 0)

    # Nếu có mô tả rõ ràng
    if any(kw in meal_text for kw in [
        "chiên", "xào", "luộc", "gà", "bò", "heo", "lợn", "thịt", "cá", "cơm", "phở", "canh", "mì", "lẩu", "hầm", "nướng", "xào"
    ]):
        return "main"
    if any(kw in meal_text for kw in [
        "chè", "sữa chua", "bánh", "kem", "flan", "trái cây", "snack", "ăn vặt", "bánh ngọt", "bánh bao", "bánh mì", "mousse", "pudding", "tiramisu", "salad trái cây", "sinh tố"
    ]):
        return "snack"

    # Nếu không có keyword rõ ràng → dùng AI
    meal_embed = model.encode(meal_text, convert_to_tensor=True)
    sim_main = util.cos_sim(meal_embed, main_embeds).max().item()
    sim_snack = util.cos_sim(meal_embed, snack_embeds).max().item()

    if sim_snack > sim_main and sim_snack > threshold:
        return "snack"
    elif sim_main > threshold:
        return "main"

    # Cuối cùng fallback về calo
    return "snack" if energy < 250 else "main"

# Gợi ý tags bằng AI
def semantic_tagging(meal, threshold=0.5):
    tags = set()
    ingredients = [ing["name"].lower() for ing in meal["ingredients"]]
    ingredient_embeddings = model.encode(ingredients, convert_to_tensor=True)

    # Gợi ý các tag như "Không gluten", "Hải sản", v.v.
    for tag, keyword_embeds in tag_embeddings.items():
        sim = util.cos_sim(ingredient_embeddings, keyword_embeds)
        if "Không" in tag:
            if not (sim > threshold).any():
                tags.add(tag)
        elif tag == "Chay":
            if not (sim > threshold).any():
                tags.add("Chay")
        else:
            if (sim > threshold).any():
                tags.add(tag)

    # Gợi ý kết hợp Á - Âu
    if "Món Á" in tags and "Món Âu hoặc khác" in tags:
        tags.add("Kết hợp Á - Âu")

    # Gợi ý allergen
    sim_allergen = util.cos_sim(ingredient_embeddings, allergen_embeddings)
    for i, allergen in enumerate(ALLERGENS):
        if (sim_allergen[:, i] > threshold).any():
            tags.add("Allergens: " + allergen)

    # Phân loại món ăn
    meal["type"] = classify_meal(meal)

    return list(tags)

# Đọc dữ liệu gốc
with open("single_meals_with_energy.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Ghi dữ liệu ra file mới
with open("meals_tagged.json", "w", encoding="utf-8") as f:
    f.write("[\n")
    for i, dish in enumerate(data):
        dish["tags"] = semantic_tagging(dish)
        json.dump(dish, f, ensure_ascii=False, indent=4)
        if i < len(data) - 1:
            f.write(",\n")
    f.write("\n]")

print("✅ Đã ghi từng món ăn vào file meals_tagged.json.")

import json

# Đọc file JSON đầu vào
with open('recipe_datas2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Lọc bỏ các bước có images rỗng cho tất cả các món
for item in data:
    item['steps'] = [step for step in item['steps'] if step['images']]

# Xuất lại dữ liệu vào file JSON
with open('filtered_meals2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Dữ liệu đã được lưu vào 'filtered_meals2.json'.")

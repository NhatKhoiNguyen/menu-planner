import json
import os

# Cấu hình
input_file = "meals_with_calories.json"   # File gốc chứa toàn bộ món ăn
output_folder = "batches"       # Thư mục lưu các batch
batch_size = 300                 # Số món mỗi batch (nên để ≤ 50 để tránh giới hạn RPD)

# Tạo thư mục nếu chưa có
os.makedirs(output_folder, exist_ok=True)

# Đọc file gốc
with open(input_file, "r", encoding="utf-8") as f:
    meals = json.load(f)

# Tách thành từng batch và lưu file
total_batches = (len(meals) + batch_size - 1) // batch_size

for i in range(total_batches):
    batch = meals[i * batch_size : (i + 1) * batch_size]
    batch_file = os.path.join(output_folder, f"meals_batch_{i + 1}.json")
    with open(batch_file, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)

print(f"✅ Đã chia thành {total_batches} batch, mỗi batch có tối đa {batch_size} món. Lưu tại thư mục '{output_folder}'")

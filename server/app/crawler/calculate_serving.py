import json
import re
import os
from fractions import Fraction

# Đọc file JSON gốc
with open("filtered_meals2.json", "r", encoding="utf-8") as f:
    dishes = json.load(f)

# Các đơn vị cần định dạng phân số
fraction_units = {"muỗng canh", "muỗng cà phê", "muỗng", "miếng", "cây", "lá", "trái", "quả", "nhánh"}

def extract_number_and_unit(amount):
    parts = amount.strip().split()
    try:
        number = float(parts[0].replace(",", "."))
        unit = " ".join(parts[1:]).lower() if len(parts) > 1 else ""
        return number, unit
    except:
        return None, None

def format_amount(number, unit):
    if unit in fraction_units:
        rounded = round(number * 4) / 4
        frac = Fraction(rounded).limit_denominator(4)
        if frac.denominator == 1:
            return f"{frac.numerator} {unit}"
        else:
            return f"{frac} {unit}"
    else:
        if number == int(number):
            return f"{int(number)} {unit}".strip()
        else:
            return f"{round(number, 2)} {unit}".strip()

# Ghi từng món vào file single_meals.json như mảng JSON
output_path = "single_meals2.json"

with open(output_path, "w", encoding="utf-8") as f:
    f.write("[\n")  # Mở đầu danh sách JSON
    first = True
    for dish in dishes:
        try:
            servings = float(dish.get("servings", 1))
            for ing in dish["ingredients"]:
                number, unit = extract_number_and_unit(ing["amount"])
                if number is not None:
                    per_serving = number / servings
                    ing["amount"] = format_amount(per_serving, unit)
            dish["servings"] = "1"

            # Ghi từng món, thêm dấu phẩy nếu không phải món đầu tiên
            if not first:
                f.write(",\n")
            f.write(json.dumps(dish, ensure_ascii=False, indent=2))
            first = False

            print(f"✅ Đã xử lý: {dish['title']}")
        except Exception as e:
            print(f"❌ Lỗi ở món '{dish.get('title', 'Không tên')}': {e}")

    f.write("\n]")

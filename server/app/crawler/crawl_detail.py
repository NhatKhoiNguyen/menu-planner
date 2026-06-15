import requests
from bs4 import BeautifulSoup
import json
import time

# Đọc file JSON chứa danh sách các URL món ăn
with open('recipe_links2.json', 'r', encoding='utf-8') as file:
    recipe_urls = json.load(file)

# Hàm crawl thông tin món ăn chi tiết từ URL
def crawl_recipe(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Tên món
        title = soup.find("h1", class_="recipe-title")
        title = title.text.strip() if title else "Không có tiêu đề"

        # 2. Nguyên liệu
        ingredients = []
        ingredient_items = soup.select(".RecipeProductsCheckboxGroup label")
        for item in ingredient_items:
            name_tag = item.find("h3", class_="recipe-ingredient--name")
            amount_tag = item.find("span", class_="recipe-ingredient--amount")
            name = name_tag.text.strip() if name_tag else ""
            amount = amount_tag.text.strip() if amount_tag else ""
            ingredients.append({"name": name, "amount": amount})

        # 3. Hướng dẫn nấu ăn
        steps = []
        instruction_blocks = soup.select(".recipe-direction")
        for block in instruction_blocks:
            step_text = ""
            images = []

            blockquote = block.find("blockquote")
            if blockquote:
                div = blockquote.find("div")
                if div:
                    step_text = div.text.strip()

                img_tags = blockquote.find_all("img")
                for img in img_tags:
                    img_url = img.get('src')
                    if img_url:
                        images.append(img_url)

            steps.append({"step": step_text, "images": images})

        # 4. Tiêu đề hướng dẫn nấu
        heading_tag = soup.find("h3", class_="recipe-direction--heading")
        heading = heading_tag.text.strip() if heading_tag else "Không có tiêu đề hướng dẫn"

        # 5. Servings
        servings = "Không có thông tin"
        nutrition_section = soup.find('section', class_='recipe-nutrition')
        if nutrition_section:
            servings_section = nutrition_section.find_all('div', class_='nut-property')
            for section in servings_section:
                label = section.find('strong')
                if label and 'Servings' in label.text:
                    val = section.find('span', class_='nut-value')
                    servings = val.text.strip() if val else servings
                    break

        # 6. Hình ảnh chính (lấy ảnh cuối trong bước nấu ăn)
        main_image = steps[-1]["images"][-1] if steps and steps[-1]["images"] else None

        return {
            "title": title,
            "servings": servings,
            "ingredients": ingredients,
            "steps": steps,
            "heading": heading,
            "main_image": main_image
        }

    except Exception as e:
        print(f"❌ Lỗi khi crawl {url}: {e}")
        with open('failed_urls.txt', 'a', encoding='utf-8') as f:
            f.write(url + '\n')
        return None

# Lưu dữ liệu vào file JSON sau mỗi món ăn được crawl
all_recipes = []
for idx, url in enumerate(recipe_urls):
    print(f"🔍 Crawling ({idx+1}/{len(recipe_urls)}): {url}")
    recipe_data = crawl_recipe(url)
    if recipe_data:
        print(f"✅ Đã crawl: {recipe_data['title']}")
        all_recipes.append(recipe_data)

        # Lưu ngay sau khi crawl mỗi món thành công
        with open('recipe_datas1.json', 'w', encoding='utf-8') as output_file:
            json.dump(all_recipes, output_file, ensure_ascii=False, indent=4)

    else:
        print(f"⚠️ Bỏ qua: {url}")
    time.sleep(1)  # nghỉ 1 giây giữa các lần crawl

print(f"📝 Đã lưu {len(all_recipes)} món vào 'recipe_datas2.json'")
print("⛔ URL lỗi được ghi vào 'failed_urls.txt'")

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import csv
import time

# Danh sách URL và nhóm thực phẩm tương 
urls = {
    "https://www.bachhoaxanh.com/sua-tuoi": "Sữa tươi",
    "https://www.bachhoaxanh.com/sua-tu-hat": "Sữa hạt",
    "https://www.bachhoaxanh.com/sua-dac": "Sữa đặc",
    "https://www.bachhoaxanh.com/bot-ngu-coc": "Yến mạch, ngũ cốc",
    "https://www.bachhoaxanh.com/kem": "Kem",
    "https://www.bachhoaxanh.com/ca-hai-san-dong-lanh": "Thịt, hải sản đông lạnh",
    "https://www.bachhoaxanh.com/thit-heo": "Thịt heo",
    "https://www.bachhoaxanh.com/thit-bo": "Thịt bò",
    "https://www.bachhoaxanh.com/thit-ga": "Thịt gà",
    "https://www.bachhoaxanh.com/ca-tom-muc-ech": "Hải sản",
    "https://www.bachhoaxanh.com/trai-cay-tuoi-ngon": "Trái cây",
    "https://www.bachhoaxanh.com/rau-sach": "Rau lá",
    "https://www.bachhoaxanh.com/cu": "Củ quả",
    "https://www.bachhoaxanh.com/nam-tuoi": "Nấm",
    "https://www.bachhoaxanh.com/gao-gao-nep": "Gạo",
    "https://www.bachhoaxanh.com/trung": "Trứng",
    "https://www.bachhoaxanh.com/xuc-xich-tuoi": "Xúc xích",
    "https://www.bachhoaxanh.com/dau-hu-dau-hu-trung": "Đậu hũ",
    "https://www.bachhoaxanh.com/sua-chua-an": "Sữa chua",
    "https://www.bachhoaxanh.com/pho-mai-an": "Bơ sữa, Phô mai",
    "https://www.bachhoaxanh.com/bun-kho": "Bún",
    "https://www.bachhoaxanh.com/mi": "Mì",
    "https://www.bachhoaxanh.com/mi-kho": "Mì khô",
    "https://www.bachhoaxanh.com/mien-kho": "Miến, phở, hủ tiếu khô",
    "https://www.bachhoaxanh.com/nui-kho": "Nui",
    "https://www.bachhoaxanh.com/dau-an": "Dầu ăn",
    "https://www.bachhoaxanh.com/nuoc-mam": "Nước mắm",
    "https://www.bachhoaxanh.com/nuoc-tuong": "Nước tương",
    "https://www.bachhoaxanh.com/duong": "Đường",
    "https://www.bachhoaxanh.com/hat-nem": "Hạt nêm",
    "https://www.bachhoaxanh.com/muoi-an": "Muối",
    "https://www.bachhoaxanh.com/tuong-ot-ca-den": "Tương ớt",
    "https://www.bachhoaxanh.com/bo": "Dầu hào, giấm, bơ thực vật",
    "https://www.bachhoaxanh.com/gia-vi-nem-san": "Gia vị nêm sẵn",
    "https://www.bachhoaxanh.com/sot-nuoc-cham": "Sốt nước chấm",
    "https://www.bachhoaxanh.com/tieu": "Tiêu",
    "https://www.bachhoaxanh.com/bot-gia-vi": "Bột gia vị",
    "https://www.bachhoaxanh.com/bot-che-bien-san": "Bột chế biến sẵn",
    "https://www.bachhoaxanh.com/banh-trang": "Bánh tráng",
    "https://www.bachhoaxanh.com/rong-bien": "Rong biển",
    "https://www.bachhoaxanh.com/nuoc-cot-dua": "Nước cốt dừa",
    "https://www.bachhoaxanh.com/dau-cac-loai": "Đậu, nấm, đồ khô",
    "https://www.bachhoaxanh.com/ca-mam": "Cá mắm, dưa mắm",
    "https://www.bachhoaxanh.com/do-chua-dua-muoi": "Đồ chua, dưa muối",
    "https://www.bachhoaxanh.com/gio-cha": "Giò chả",
    "https://www.bachhoaxanh.com/mat-ong": "Mật ong",
    "https://www.bachhoaxanh.com/banh-ngot": "Bánh ngọt",
    "https://www.bachhoaxanh.com/cac-loai-hat": "Hạt khô",
}

# Cấu hình trình duyệt headless
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Mở file CSV để ghi kết quả
with open("ingredient_prices3.csv", mode="w", newline='', encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["Tên sản phẩm", "Giá (đồng)", "Đơn vị", "Nhóm thực phẩm"])

    for url, category in urls.items():
        print(f"Đang crawl: {url} ({category})")
        driver.get(url)

        # Đợi sản phẩm đầu tiên xuất hiện
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "box_product"))
        )

        # Cuộn từng bước để tải toàn bộ sản phẩm
        scroll_pause_time = 5
        max_scroll_attempts = 5  # tránh lặp vô hạn
        previous_count = 0
        scroll_attempts = 0

        while scroll_attempts < max_scroll_attempts:
            driver.execute_script("window.scrollBy(0, 500);")  # cuộn từng đoạn nhỏ
            time.sleep(scroll_pause_time)
            
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            products = soup.select(".box_product")
            current_count = len(products)

            if current_count == previous_count:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
                previous_count = current_count

        print(f"✅ Đã tải tổng cộng {current_count} sản phẩm.")



        seen = set()
        for product in products:
            name_el = product.select_one(".product_name")
            name = name_el.text.strip() if name_el else "Không rõ tên"

            price = None
            unit = None

            price_el = product.select_one(".product_price")
            if price_el:
                price_text = price_el.text.strip()
                price_text = price_text.replace('.', '')  # chuẩn hóa giá: 17.500 → 17500
                match = re.search(r"(\d+)đ\s*/\s*([\d\.]+)?\s*(kg|g|l|ml|trái|củ)?", price_text)
                if match:
                    price = match.group(1)
                    amount = match.group(2) or "1"
                    unit_type = match.group(3) or ""
                    unit = f"{amount}{unit_type}"
                else:
                    # Không có đơn vị trong product_price → thử lấy từ product_name
                    price = re.sub(r"[^\d]", "", price_text)  # chỉ lấy số trong giá (loại bỏ 'đ', 'k',...)
                    unit_match = re.search(r"(\d+\.?\d*)\s?(kg|g|l|ml|trái|củ|quả)", name.lower())
                    if unit_match:
                        amount = unit_match.group(1)
                        unit_type = unit_match.group(2)
                        unit = f"{amount}{unit_type}"
                    else:
                        unit = "Không rõ"

            key = f"{name}-{price}-{unit}"
            if price and unit and key not in seen:
                seen.add(key)
                writer.writerow([name, price, unit, category])
                print(f"{name}: {price}đ/{unit} ({category})")

driver.quit()

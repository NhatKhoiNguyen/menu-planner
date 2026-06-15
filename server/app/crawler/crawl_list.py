from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json

# Setup trình duyệt
options = Options()
# options.add_argument("--headless")  # Mở nếu muốn chạy ẩn
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Truy cập trang đầu tiên
base_url = "https://kingfoodmart.com/bai-viet?category=recipe&lv=cate"
driver.get(base_url)
time.sleep(2)

def scroll_to_bottom(driver):
    scroll_pause_time = 1
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def close_popup_if_exists(driver):
    try:
        popup_close = driver.find_element(By.CSS_SELECTOR, ".ant-modal-close")
        popup_close.click()
        time.sleep(1)
        print("⛔ Popup đã được đóng.")
    except NoSuchElementException:
        pass

# Tập hợp link đã thu thập
all_links = set()
page = 1

while True:
    print(f"\n📄 Đang xử lý trang {page}...")

    scroll_to_bottom(driver)
    close_popup_if_exists(driver)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Lấy các link công thức từ trang hiện tại
    recipe_links = soup.select("a.flex.flex-col.gap-4.pb-2[href]")
    new_links = 0
    for link in recipe_links:
        full_url = "https://kingfoodmart.com" + link['href']
        if full_url not in all_links:
            all_links.add(full_url)
            print("✅", full_url)
            new_links += 1

    if new_links == 0:
        print("⚠️ Không có liên kết mới. Có thể đang ở trang cuối.")
    
    # Tìm và click nút "Trang tiếp theo" nếu có
    next_li = soup.select_one("li.ant-pagination-next[aria-disabled='false']")
    if next_li:
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.ant-pagination-next button")
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            ActionChains(driver).move_to_element(next_button).pause(1).click().perform()
            time.sleep(2)
            page += 1
        except (ElementClickInterceptedException, NoSuchElementException) as e:
            print("❌ Không thể click nút tiếp theo:", e)
            break
    else:
        print("🏁 Đã tới trang cuối.")
        break

# Đóng trình duyệt
driver.quit()

# Ghi file JSON
output_file = "recipe_links.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(list(all_links), f, ensure_ascii=False, indent=2)

print(f"\n🎉 Đã lưu {len(all_links)} liên kết vào '{output_file}'")

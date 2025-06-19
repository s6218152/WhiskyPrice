

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv

BASE_URLS = [
    "https://www.609.com.tw/ProductList/%E9%BA%A5%E5%8D%A1%E5%80%AB",
    "https://www.609.com.tw/ProductList/%E7%99%BE%E5%AF%8C",
    "https://www.609.com.tw/ProductList/%E7%9A%87%E5%AE%B6%E7%A6%AE%E7%82%AE",
    "https://www.609.com.tw/ProductList/%E6%85%95%E8%B5%AB",
    "https://www.609.com.tw/ProductList/%E5%A4%A7%E6%91%A9",
    "https://www.609.com.tw/ProductList/%E7%B4%84%E7%BF%B0%E8%B5%B0%E8%B7%AF",
    "https://www.609.com.tw/ProductList/%E6%A0%BC%E8%98%AD%E8%8F%B2%E8%BF%AA",
    "https://www.609.com.tw/ProductList/%E5%B1%B1%E5%B4%8E",
    "https://www.609.com.tw/ProductList/%E9%9F%BF",
    "https://www.609.com.tw/ProductList/%E4%BD%99%E5%B8%82",
    "https://www.609.com.tw/ProductList/%E6%B3%A2%E6%91%A9",
    "https://www.609.com.tw/ProductList/%E6%A0%BC%E8%98%AD%E8%B7%AF%E6%80%9D"
]

def parse_products(container):
    products = []
    rows = container.find_elements(By.CSS_SELECTOR, "div.row")
    for row in rows:
        for prod in row.find_elements(By.CSS_SELECTOR, "div"):
            try:
                name = prod.find_element(By.CSS_SELECTOR, "div.card-heading.mt-3 > h6").text.strip()
                price = prod.find_element(By.CSS_SELECTOR, "div.card-body > div.text-center").text.strip()
                if name != "N/A" and price != "N/A":
                    products.append((name, price.split('\n')[0].strip()))
            except Exception:
                continue
    return products

def fetch_all_products(urls):
    chrome_options = Options()
    chrome_options.add_argument('--headless') 
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    all_products = []
    try:
        for url in urls:
            print(f"[DEBUG] driver.get: {url}")
            driver.get(url)
            try:
                # 顯式等待直到元素出現
                wait = WebDriverWait(driver, 15)
                container = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#PartList > div.container"))
                )
                all_products.extend(parse_products(container))
            except Exception as e:
                print(f"[ERROR] 無法解析 {url}: {e}")
    finally:
        driver.quit()
    return all_products

def main():
    all_products = fetch_all_products(BASE_URLS)
    seen = set()
    unique_products = []
    for name, member_price in all_products:
        key = (name, member_price)
        if key not in seen:
            print(f"品名: {name}\t會員價: {member_price}")
            unique_products.append({"品名": name, "會員價": member_price})
            seen.add(key)
    # 輸出成 CSV 檔
    with open("products.csv", "w", newline='', encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["品名", "會員價"])
        writer.writeheader()
        writer.writerows(unique_products)

if __name__ == "__main__":
    main()

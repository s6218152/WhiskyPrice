

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import requests
import json
import urllib.parse

def get_dynamic_urls():
    """
    從 609.com.tw 取得品牌資料並動態產生商品列表的 URL。
    """
    source_url = "https://www.609.com.tw/Parts/GetBrandList?id=1101%E8%98%87%E6%A0%BC%E8%98%AD"
    product_base_url = "https://www.609.com.tw/ProductList/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    base_urls = []
    
    try:
        print("正在動態獲取最新的 URL 列表...")
        response = requests.get(source_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        brand_names = response.json()
        
        if not brand_names:
            print("注意：從 API 取得的品牌資料為空。")
            return []

        base_urls = [f"{product_base_url}{urllib.parse.quote(name)}" for name in brand_names]
        print(f"成功獲取 {len(base_urls)} 個 URL。")
        
    except requests.exceptions.RequestException as e:
        print(f"取得動態 URL 時發生網路錯誤: {e}")
    except json.JSONDecodeError:
        print("解析動態 URL 的 JSON 資料時發生錯誤。")
        
    return base_urls

BASE_URLS = get_dynamic_urls()

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

import time
import csv
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def create_driver():
    options = uc.ChromeOptions()
    # options.add_argument("--headless=new")  # Comment out if you want to see browser
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # options.add_experimental_option("prefs", prefs)
    options.page_load_strategy = "eager" 
    driver = uc.Chrome(options=options)
    return driver

def extract_walmart_data(driver, url):
    print(f"Opening Walmart product page: {url}")
    try:
        driver.get(url)
        time.sleep(3)
    except Exception as e:
        print(f"Error opening Walmart page {url}: {e}")
        return None, None, None, None, None

    try:
        title = driver.find_element(By.CSS_SELECTOR, 'h1').text
    except Exception:
        title = "N/A"

    try:
        brand = driver.find_element(By.CSS_SELECTOR, '[data-automation-id="product-brand-name"]').text
    except Exception:
        brand = "N/A"

    try:
        model = driver.find_element(By.CSS_SELECTOR, '[data-automation-id="product-mpn"]').text
    except Exception:
        model = "N/A"

    try:
        price_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//span[@itemprop='price']"))
        )
        price = price_element.text.strip()
        print("Price:", price)
    except Exception:   
        price = "N/A"

    try:
        image_element = driver.find_element(By.CSS_SELECTOR, '#maincontent section img')
        image_url = image_element.get_attribute('src')
        if not image_url or image_url.strip() == "" or image_url.startswith("data:") or image_url == "about:blank":
            raise Exception("Invalid image src")
    except Exception:
        image_url = "N/A"
    # print(image_url)
    return title, brand, model, price, image_url


def search_amazon(driver, title, brand):
    print(f"Searching on Google: {title}")
    driver.get("https://www.google.com/ncr")  # "ncr" = no country redirect
    time.sleep(2)

    # Try to accept cookies
    try:
        agree_button = driver.find_element(By.XPATH, '//button/div[contains(text(),"Accept all")]')
        agree_button.click()
        print("Accepted Google cookies.")
        time.sleep(2)
    except Exception:
        pass  # No popup

    search_box = driver.find_element(By.NAME, "q")
    search_box.clear()
    search_box.send_keys(f"{title} amazon.com")
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    amazon_link = None

    try:
        # Only pick links where the text is from search results (h3 inside a)
        results = driver.find_elements(By.XPATH, '//a/h3/..')
        for result in results:
            href = result.get_attribute('href')
            if href and 'amazon.com' in href:
                amazon_link = href
                break
    except Exception as e:
        print(f"Error fetching search results: {e}")

    if amazon_link:
        print(f"Opening Amazon page: {amazon_link}")
        try:
            driver.get(amazon_link)
            time.sleep(3)
        except Exception as e:
            print(f"Error opening Amazon page {amazon_link}: {e}")

    return amazon_link if amazon_link else "Not Found"

def process_walmart_links(urls):
    driver = create_driver()
    results = []

    for url in urls:
        try:
            title, brand, model, price, image_url = extract_walmart_data(driver, url)
            amazon_url = search_amazon(driver, title, brand)

            results.append({
                "walmart_url": url,
                "title": title,
                "brand": brand,
                "model": model,
                "price": price,
                "image_url": image_url,
                "amazon_url": amazon_url
            })
        except Exception as e:
            print(f"Error processing {url}: {e}")
            results.append({
                "walmart_url": url,
                "title": "Error",
                "brand": "Error",
                "model": "Error",
                "price": "Error",
                "image_url": "Error",
                "amazon_url": "Error"
            })

    driver.quit()
    return results

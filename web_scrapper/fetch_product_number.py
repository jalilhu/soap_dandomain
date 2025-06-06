from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import time
import os
chromedriver_path = (r"C:\Users\tri-l\OneDrive\Jalil_Tasks\Insert_New_Product_INK_HOUSE\Project\web_scrapper\chromedriver.exe")  # if chromedriver is in PATH, else put full path here
chrome_binary_path = r"C:\Users\tri-l\Downloads\chrome-win32\chrome-win32\chrome.exe"  # example

user_name = os.getenv("DESPEC_USERNAME", "your_username")  # Replace with your actual username
password_str = os.getenv("DESPEC_PASSWORD", "your_password")  # Replace with your actual password

print("Using username:", user_name)
print("Using password:", password_str)


def open_homepage():
    # Adjust path to chromedriver if needed
   

    # options.add_argument("--headless")  # uncomment if you want headless mode (no visible window)
    
    driver =create_driver()
    
    url = "https://www.despec.dk/"
    driver.get(url)
    
    print("Page title:", driver.title)
    
    # Example: get some text from homepage (adjust selector accordingly)
    try:
        elem = driver.find_element(By.TAG_NAME, "h1")
        print("H1 on homepage:", elem.text)
    except Exception as e:
        print("Could not find h1 element:", e)
    
    # wait so you can see the browser (remove for headless or automation)
    time.sleep(5)
    
    driver.quit()


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--no-sandbox')
    options.binary_location = chrome_binary_path
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login():
    """Perform login on Despec Denmark website using Selenium driver."""
    driver = create_driver()
    driver.get("https://www.despec.dk/")  # Replace with the actual login URL

    wait = WebDriverWait(driver, 10)
    try:
        wait.until(lambda d: d.current_url != "https://www.despec.dk")
        login_toggle = wait.until(EC.element_to_be_clickable((By.ID, "login-dropdown-toggle")))
        login_toggle.click()

        username = wait.until(EC.visibility_of_element_located((By.ID, "username")))
        username.clear()
        username.send_keys(user_name)

        pwd_input = wait.until(EC.visibility_of_element_located((By.ID, "password")))
        pwd_input.clear()
        pwd_input.send_keys(password_str)

        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#login-form button[type='submit']")))
        login_button.click()

        # Wait for an element that appears only after login — example:
        # Let's say after login, a logout button with id 'logout-btn' appears
        wait.until(EC.presence_of_element_located((By.ID, "logoff")))
        search_product(driver, "hp 937")
        print("✅ Login successful.")
        return True

    except TimeoutException:
        print("❌ Login failed or took too long.")
        return False
    
def search_product(driver, product_title):
    wait = WebDriverWait(driver, 20)

    # Wait for the search input to be clickable
    search_input = wait.until(
        EC.element_to_be_clickable((By.ID, "search-input-desktop"))
    )
    
    search_input.clear()
    search_input.send_keys(product_title)
    search_input.send_keys(Keys.RETURN)  # Press Enter to submit search

    # Wait for search results to appear - adjust selector if needed
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results, .product-list, .result-item"))
    )
    get_prooduct_value(driver)
   
def get_prooduct_value(driver):
    wait = WebDriverWait(driver, 10)
    try:
        first_product_row = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".product-row")))
        product_id = first_product_row.get_attribute("data-product-id")
        print(f"✅ Found product ID: {product_id}")
        
        product_rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-row")))
        for idx, product_row in enumerate(product_rows, start=1):
            product_id = product_row.get_attribute("data-product-id")
            print(f"Product #{idx} ID: {product_id}")
    except TimeoutException:
        print("❌ Could not find product number element.")
        return None

import os
import streamlit as st
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc

# Function to initialize undetected Chrome driver
def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return uc.Chrome(options=options)

# Function to fetch "From Latest DrawNo" result
def get_from_latest_drawno(number_to_search: str) -> str:
    url = "https://www.4d2u.com/search.php"
    try:
        driver = get_driver()
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Input number
        search_input = wait.until(EC.presence_of_element_located((By.NAME, "search")))
        search_input.clear()
        search_input.send_keys(number_to_search)

        # Uncheck MAG
        mag_checkbox = driver.find_element(By.NAME, "mag")
        if mag_checkbox.is_selected():
            mag_checkbox.click()

        # Check SIN
        sin_checkbox = driver.find_element(By.NAME, "sin")
        if not sin_checkbox.is_selected():
            sin_checkbox.click()

        # Select permutation mode "No"
        no_permutation = driver.find_element(By.XPATH, '//input[@name="mode" and @value="exa"]')
        no_permutation.click()

        # Submit form
        search_button = driver.find_element(By.NAME, "SearchAction")
        search_button.click()

        # Wait and extract "From Latest DrawNo"
        from_latest_label = wait.until(
            EC.presence_of_element_located((By.XPATH, "//td[normalize-space()='From Latest DrawNo']"))
        )
        from_latest_value_td = from_latest_label.find_element(By.XPATH, "./following-sibling::td")
        result = from_latest_value_td.text.strip()

        driver.quit()
        return result

    except TimeoutException:
        return "❌ Timeout waiting for page elements."
    except WebDriverException as e:
        return f"❌ WebDriver error: {e}\n\nTraceback:\n{traceback.format_exc()}"
    except Exception as e:
        return f"❌ Unexpected error: {e}\n\nTraceback:\n{traceback.format_exc()}"
    finally:
        try:
            driver.quit()
        except:
            pass

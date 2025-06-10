import os
import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import traceback

# Configure Chrome for headless environment (Streamlit Cloud compatible)
def get_driver():
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = "/usr/bin/chromium"  # For Streamlit Cloud
    return uc.Chrome(options=options, headless=True)

def get_from_latest_drawno(number_to_search: str) -> str:
    """Scrape 'From Latest DrawNo' value from 4d2u.com for the given number."""
    url = "https://www.4d2u.com/search.php"
    driver = None
    try:
        driver = get_driver()
        driver.get(url)

        wait = WebDriverWait(driver, 20)

        # Input number
        search_input = wait.until(EC.visibility_of_element_located((By.NAME, "search")))
        search_input.clear()
        search_input.send_keys(number_to_search)

        # Ensure correct checkboxes
        mag_checkbox = driver.find_element(By.NAME, "mag")
        if mag_checkbox.is_selected():
            mag_checkbox.click()

        sin_checkbox = driver.find_element(By.NAME, "sin")
        if not sin_checkbox.is_selected():
            sin_checkbox.click()

        # Set permutation mode to exact
        no_perm = driver.find_element(By.XPATH, '//input[@name="mode" and @value="exa"]')
        no_perm.click()

        # Submit form
        driver.find_element(By.NAME, "SearchAction").click()

        # Extract "From Latest DrawNo"
        from_latest_label = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//td[normalize-space()='From Latest DrawNo']")
        ))
        value_td = from_latest_label.find_element(By.XPATH, "./following-sibling::td")
        return value_td.text.strip()

    except TimeoutException:
        return "❌ Timeout waiting for page elements."
    except WebDriverException as e:
        return f"❌ WebDriver error: {e}\n\nTraceback:\n{traceback.format_exc()}"
    except Exception as e:
        return f"❌ Unexpected error: {e}\n\nTraceback:\n{traceback.format_exc()}"
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
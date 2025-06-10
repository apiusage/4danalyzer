import os
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import traceback

# Set up Chrome for Streamlit Cloud
chrome_options = Options()
chrome_options.binary_location = "/usr/bin/chromium"
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
os.environ["PATH"] += os.pathsep + "/usr/lib/chromium"

def get_from_latest_drawno(number_to_search: str) -> str:
    """Scrape 'From Latest DrawNo' value from 4d2u.com for the given number."""
    url = "https://www.4d2u.com/search.php"
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)

        wait = WebDriverWait(driver, 10)

        # Fill in number
        search_input = wait.until(EC.presence_of_element_located((By.NAME, "search")))
        search_input.clear()
        search_input.send_keys(number_to_search)

        # Uncheck "MAG" if selected
        mag_checkbox = driver.find_element(By.NAME, "mag")
        if mag_checkbox.is_selected():
            mag_checkbox.click()

        # Check "SIN" if not selected
        sin_checkbox = driver.find_element(By.NAME, "sin")
        if not sin_checkbox.is_selected():
            sin_checkbox.click()

        # Select "No" for Permutation
        no_permutation = driver.find_element(By.XPATH, '//input[@name="mode" and @value="exa"]')
        no_permutation.click()

        # Submit form
        search_button = driver.find_element(By.NAME, "SearchAction")
        search_button.click()

        # Scrape "From Latest DrawNo"
        from_latest_label = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//td[normalize-space()='From Latest DrawNo']")
        ))
        from_latest_value_td = from_latest_label.find_element(By.XPATH, "./following-sibling::td")
        from_latest_value = from_latest_value_td.text.strip()

        driver.quit()
        return from_latest_value

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
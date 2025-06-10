import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import traceback

def get_from_latest_drawno(number_to_search: str) -> str:
    """Scrape 'From Latest DrawNo' value from 4d2u.com for the given number."""
    url = "https://www.4d2u.com/search.php"

    # Configure Chrome options
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--headless=new")  # use --headless=new for Chrome 109+
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

    try:
        # Use version_main to help uc find correct driver
        driver = uc.Chrome(options=chrome_options)
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

        return from_latest_value

    except TimeoutException:
        return "Timeout waiting for elements."
    except WebDriverException as e:
        return f"WebDriver error: {e}\nTraceback:\n{traceback.format_exc()}"
    except Exception as e:
        return f"Unexpected error: {e}\nTraceback:\n{traceback.format_exc()}"
    finally:
        try:
            driver.quit()
        except:
            pass

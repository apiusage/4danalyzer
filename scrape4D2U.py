import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_from_latest_drawno(number: str) -> str:
    url = f"https://www.4d2u.com/search.php?s=&lang=E&search={number}&from_day=01&from_month=01&from_year=1985&to_day=11&to_month=06&to_year=2025&sin=Y&mode=exa&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"

    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

    driver = uc.Chrome(options=options)

    try:
        driver.get(url)

        # Wait until a table is loaded or timeout
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//table"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")

        rows = soup.select("table tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)
                if "from latest drawno" in label:
                    return value

        return "From Latest DrawNo not found"

    except Exception as e:
        return f"Error: {e}"

    finally:
        driver.quit()

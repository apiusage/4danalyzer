import undetected_chromedriver as uc
from bs4 import BeautifulSoup
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

    driver = uc.Chrome(options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table"))
        )
    except:
        print("Table not found or timed out.")
        driver.quit()
        return "Not found"

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # Optional: debug output
    print(soup.prettify()[:1000])

    rows = soup.select("table tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 2:
            label = cells[0].get_text(strip=True).lower()
            value = cells[1].get_text(strip=True)
            if "from latest drawno" in label:
                return value

    return "Not found"

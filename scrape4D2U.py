from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def get_from_latest_drawno(number: str, permutation: str) -> str:
    # Prepare date values
    today = datetime.today()
    to_day = today.day
    to_month = today.month
    to_year = today.year

    # Construct URL based on permutation
    if permutation == "no":
        url = f"https://www.4d2u.com/search.php?s=&lang=E&search={number}&from_day=01&from_month=01&from_year=1985&to_day={to_day:02d}&to_month={to_month:02d}&to_year={to_year}&sin=Y&mode=exa&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"
    elif permutation == "yes":
        url = f"https://www.4d2u.com/search.php?s=&lang=E&search={number}&from_day=01&from_month=01&from_year=1985&to_day={to_day:02d}&to_month={to_month:02d}&to_year={to_year}&sin=Y&mode=per&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"
    else:
        return "Invalid permutation parameter"

    # Configure headless Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)

        # Wait for Cloudflare challenge & JS to complete
        time.sleep(7)  # Adjust this if needed

        # Get page source after JS rendered
        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")

        for row in soup.select("table tr"):
            cells = row.find_all("td")
            if len(cells) == 2:
                label = cells[0].get_text(strip=True).lower()
                if "from latest drawno" in label:
                    return cells[1].get_text(strip=True)

        return "Not found"

    finally:
        driver.quit()

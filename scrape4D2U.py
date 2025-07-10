import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
import time
from requests.exceptions import ReadTimeout

def get_from_latest_drawno(number: str, permutation: str, retries=3, delay=5) -> str:
    t = datetime.today()
    mode = 'per' if permutation == 'yes' else 'exa'
    url = f"https://www.4d2u.com/search.php?s=&lang=E&search={number}&from_day=01&from_month=01&from_year=1985&to_day={t.day:02d}&to_month={t.month:02d}&to_year={t.year}&sin=Y&mode={mode}&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"

    scraper = cloudscraper.create_scraper()

    for attempt in range(retries):
        try:
            r = scraper.get(url, timeout=10)
            if r.status_code != 200:
                return f"HTTP error {r.status_code}"
            soup = BeautifulSoup(r.content, "html.parser")
            for row in soup.select("table tr"):
                tds = row.find_all("td")
                if len(tds) == 2 and "from latest drawno" in tds[0].text.lower():
                    return tds[1].text.strip()
            return "Data not found"
        except ReadTimeout:
            if attempt < retries - 1:
                time.sleep(delay)  # wait before retrying
            else:
                return "Request timed out after multiple retries"
        except Exception as e:
            return f"Error: {e}"

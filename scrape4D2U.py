import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
import time

def get_from_latest_drawno(number: str) -> str:
    url = "https://www.4d2u.com/search.php"
    params = {
        "s": "",
        "lang": "E",
        "search": number,
        "from_day": "01",
        "from_month": "01",
        "from_year": "1985",
        "to_day": "11",
        "to_month": "06",
        "to_year": "2025",
        "sin": "Y",
        "mode": "exa",
        "pri_top": "Y",
        "pri_sta": "Y",
        "pri_con": "Y",
        "graph": "N",
        "SearchAction": "Search"
    }

    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        ]),
        "Referer": "https://www.4d2u.com/",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }

    # Setup retry logic
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        # Optional: wait a random short time to mimic human behavior
        time.sleep(random.uniform(1.0, 2.5))

        response = session.get(url, params=params, headers=headers, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the exact value
        rows = soup.select("table tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 2:
                label = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                if label == "From Latest DrawNo":
                    return value
        return "Not found"

    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

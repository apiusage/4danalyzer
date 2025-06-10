import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

    # Setup retry logic
    session = requests.Session()
    retry = Retry(
        total=5,                # Retry up to 5 times
        backoff_factor=2,       # Wait 2, 4, 8, 16... seconds
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        response = session.get(url, params=params, timeout=30)
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

import streamlit as st
import pandas as pd
import time
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from requests.exceptions import ReadTimeout, RequestException

def get_from_latest_drawno(number: str, permutation: str, retries=3, delay=3):
    """Fetch 'From Latest DrawNo' for a given 4D number."""
    t = datetime.today()
    mode = 'per' if permutation == 'yes' else 'exa'
    url = (
        f"https://www.4d2u.com/search.php?s=&lang=E&search={number}"
        f"&from_day=01&from_month=01&from_year=1985"
        f"&to_day={t.day:02d}&to_month={t.month:02d}&to_year={t.year}"
        f"&sin=Y&mode={mode}&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"
    )

    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )

    for attempt in range(retries):
        try:
            r = scraper.get(url, timeout=60)

            if r.status_code != 200:
                return {"digit": number, "From Latest DrawNo": f"HTTP {r.status_code}", "url": url}

            soup = BeautifulSoup(r.content, "lxml")  # lxml is 5x faster than html.parser

            for row in soup.select("table tr"):
                tds = row.find_all("td")
                if len(tds) == 2 and "from latest drawno" in tds[0].text.lower():
                    return {"digit": number, "From Latest DrawNo": tds[1].text.strip(), "url": url}

            return {"digit": number, "From Latest DrawNo": "Data not found", "url": url}

        except ReadTimeout:
            if attempt < retries - 1:
                time.sleep(delay)
        except (RequestException, Exception) as e:
            return {"digit": number, "From Latest DrawNo": f"Error: {e}", "url": url}

    return {"digit": number, "From Latest DrawNo": "Failed after retries", "url": url}
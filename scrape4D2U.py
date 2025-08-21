import streamlit as st
import pandas as pd
import time
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from requests.exceptions import ReadTimeout, RequestException

# -------------------------
# Scraper Function
# -------------------------
def get_from_latest_drawno(number: str, permutation: str, retries=3, delay=3):
    """
    Fetch 'From Latest DrawNo' for a given 4D number.
    """
    t = datetime.today()
    mode = 'per' if permutation == 'yes' else 'exa'
    url = (
        f"https://www.4d2u.com/search.php?"
        f"s=&lang=E&search={number}&from_day=01&from_month=01&from_year=1985"
        f"&to_day={t.day:02d}&to_month={t.month:02d}&to_year={t.year}"
        f"&sin=Y&mode={mode}&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"
    )

    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/115.0.0.0 Safari/537.36',
        'Referer': 'https://www.4d2u.com/',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    for attempt in range(retries):
        try:
            r = scraper.get(url, headers=headers, timeout=20)
            if r.status_code != 200:
                return {"digit": number, "From Latest DrawNo": f"HTTP {r.status_code}", "url": url}

            soup = BeautifulSoup(r.content, "html.parser")
            for row in soup.select("table tr"):
                tds = row.find_all("td")
                if len(tds) == 2 and "from latest drawno" in tds[0].text.lower():
                    return {"digit": number, "From Latest DrawNo": tds[1].text.strip(), "url": url}

            return {"digit": number, "From Latest DrawNo": "Data not found", "url": url}

        except ReadTimeout:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return {"digit": number, "From Latest DrawNo": "Request timed out", "url": url}

        except RequestException as re:
            return {"digit": number, "From Latest DrawNo": f"Request error: {re}", "url": url}

        except Exception as e:
            return {"digit": number, "From Latest DrawNo": f"Error: {e}", "url": url}

    return {"digit": number, "From Latest DrawNo": "Failed after retries", "url": url}
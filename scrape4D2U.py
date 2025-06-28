import streamlit as st
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def get_from_latest_drawno(number: str, permutation: str) -> str:
    today = datetime.today()
    to_day = today.day
    to_month = today.month
    to_year = today.year

    if permutation == "no":
        url = f"https://www.4d2u.com/search.php?s=&lang=E&search={number}&from_day=01&from_month=01&from_year=1985&to_day={to_day:02d}&to_month={to_month:02d}&to_year={to_year}&sin=Y&mode=exa&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"
    elif permutation == "yes":
        url = f"https://www.4d2u.com/search.php?s=&lang=E&search={number}&from_day=01&from_month=01&from_year=1985&to_day={to_day:02d}&to_month={to_month:02d}&to_year={to_year}&sin=Y&mode=per&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"
    else:
        return "Invalid permutation parameter"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.4d2u.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200 or "Attention Required" in response.text:
        st.warning("Blocked by Cloudflare or access denied")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    for row in soup.select("table tr"):
        cells = row.find_all("td")
        if len(cells) == 2:
            label = cells[0].get_text(strip=True).lower()
            if "from latest drawno" in label:
                return cells[1].get_text(strip=True)

    return "Not found"
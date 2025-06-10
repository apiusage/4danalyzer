import requests
from bs4 import BeautifulSoup
import streamlit as st

def get_from_latest_drawno(number: str) -> str:
    url = f"https://www.4d2u.com/search.php?s=&lang=E&search={number}&from_day=01&from_month=01&from_year=1985&to_day=11&to_month=06&to_year=2025&sin=Y&mode=exa&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    st.write("Status code:", response.status_code)
    st.code(response.text[:1000])
    soup = BeautifulSoup(response.content, "html.parser")

    for row in soup.select("table tr"):
        cells = row.find_all("td")
        if len(cells) == 2:
            label = cells[0].get_text(strip=True).lower()
            if "from latest drawno" in label:
                return cells[1].get_text(strip=True)
    return "Not found"

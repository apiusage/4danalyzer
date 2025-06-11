from datetime import datetime
import requests
from bs4 import BeautifulSoup

def get_from_latest_drawno(number: str, permutation: str) -> str:
    # Get today's date
    today = datetime.today()
    to_day = today.day
    to_month = today.month
    to_year = today.year

    # Use formatted values in the URL
    if permutation == "no":
        url = f"https://www.4d2u.com/search.php?s=&lang=E&search={number}&from_day=01&from_month=01&from_year=1985&to_day={to_day:02d}&to_month={to_month:02d}&to_year={to_year}&sin=Y&mode=exa&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"
    elif permutation == "yes":
        url = f"https://www.4d2u.com/search.php?s=&lang=E&search={number}&from_day=01&from_month=01&from_year=1985&to_day={to_day:02d}&to_month={to_month:02d}&to_year={to_year}&sin=Y&mode=per&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    for row in soup.select("table tr"):
        cells = row.find_all("td")
        if len(cells) == 2:
            label = cells[0].get_text(strip=True).lower()
            if "from latest drawno" in label:
                return cells[1].get_text(strip=True)
    return "Not found"

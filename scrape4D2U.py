import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_from_latest_drawno(number: str, permutation: str) -> str:
    t = datetime.today()
    mode = 'per' if permutation == 'yes' else 'exa'
    url = f"https://www.4d2u.com/search.php?s=&lang=E&search={number}&from_day=01&from_month=01&from_year=1985&to_day={t.day:02d}&to_month={t.month:02d}&to_year={t.year}&sin=Y&mode={mode}&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"

    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code != 200 or "Attention Required" in r.text:
            return "Blocked by Cloudflare or access denied"
        for row in BeautifulSoup(r.content, "html.parser").select("table tr"):
            tds = row.find_all("td")
            if len(tds) == 2 and "from latest drawno" in tds[0].text.lower():
                return tds[1].text.strip()
    except:
        pass
    return "Blocked by Cloudflare or access denied"
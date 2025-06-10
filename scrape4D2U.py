import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

def get_from_latest_drawno(number: str) -> str:
    url = f"https://www.4d2u.com/search.php?s=&lang=E&search={number}&from_day=01&from_month=01&from_year=1985&to_day=11&to_month=06&to_year=2025&sin=Y&mode=exa&pri_top=Y&pri_sta=Y&pri_con=Y&graph=N&SearchAction=Search"

    # Setup Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--user-agent=Mozilla/5.0")

    # Start browser
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)
    time.sleep(3)

    # Extract page source
    html = driver.page_source
    status_code = driver.execute_script("return document.readyState")  # This will show 'complete'
    driver.quit()

    # Show simulated response info
    st.write("Simulated Page Load Status:", status_code)
    st.code(html[:1000], language="html")  # First 1000 chars of the HTML page

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    for row in soup.select("table tr"):
        cells = row.find_all("td")
        if len(cells) == 2:
            label = cells[0].get_text(strip=True).lower()
            if "from latest drawno" in label:
                return cells[1].get_text(strip=True)
    return "Not found"
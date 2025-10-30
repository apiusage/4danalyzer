import random, string, platform
import streamlit as st
from st_copy import copy_button
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

try:
    from faker import Faker
    faker = Faker()
except:
    faker = None

# ---------------- CONFIG ----------------
PAGE_URL = "https://4dinsingapore.com/amember/signup"
HEADLESS = True
IMPLICIT_WAIT = 6
RANDOMIZE_COUNTRY = True
DEFAULT_COUNTRY_CODE = "SG"

# ---------------- HELPERS ----------------
def copy_text(label, text):
    copy_button(text, tooltip=f"Copy {label}", copied_label="Copied!", icon="st")

def rand_username(min_len=6, max_len=8):
    base = (faker.word() if faker else random.choice([
        "silver","monkey","dragon","shadow","forest","candle","rocket",
        "tiger","purple","pencil","planet","green","stone","magic","cloud","flame"
    ])).lower()
    base += ''.join(random.choice(string.ascii_lowercase) for _ in range(max(0,min_len-len(base))))
    base = base[:max_len]
    return base + ''.join(random.choice(string.digits) for _ in range(random.choice([2,3])))

def rand_email(name_hint=None):
    name = (faker.user_name() if faker else (name_hint or "user")) + str(random.randint(100,999))
    return f"{name}@{random.choice(['outlook.com','gmail.com','yahoo.com','hotmail.com','mailinator.com'])}"

def rand_name():
    if faker: return faker.name()
    return f"{random.choice(['Alex','Sam','Jamie','Taylor','Chris','Jordan','Morgan'])} {random.choice(['Lee','Tan','Ng','Lim','Wong','Smith','Chen'])}"

def choose_country(select_elem):
    opts = [o.get_attribute("value") for o in select_elem.options if o.get_attribute("value")]
    if not opts: return DEFAULT_COUNTRY_CODE
    return random.choice(opts) if RANDOMIZE_COUNTRY else (DEFAULT_COUNTRY_CODE if DEFAULT_COUNTRY_CODE in opts else opts[0])

# ---------------- BROWSER ----------------
def setup_driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--remote-allow-origins=*")
    opts.add_experimental_option("detach", True)
    if platform.system() != "Windows": opts.binary_location="/usr/bin/chromium"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.implicitly_wait(IMPLICIT_WAIT)
    return driver

def run_browser():
    driver = setup_driver()
    driver.get(PAGE_URL)
    wait = WebDriverWait(driver, 12)

    # Select product
    try: driver.find_element(By.ID,"product-3-3").click()
    except:
        radios = driver.find_elements(By.CSS_SELECTOR,"input[type='radio'][name^='product_id_page-0']")
        if radios: radios[0].click()

    # Generate credentials
    full_name, username, email, password = rand_name(), rand_username(), rand_email(), "111111"
    driver.find_element(By.NAME,"_name").send_keys(full_name)
    driver.find_element(By.NAME,"email").send_keys(email)
    driver.find_element(By.NAME,"login").send_keys(username)
    driver.find_element(By.NAME,"pass").send_keys(password)

    # Select country
    try:
        sel = Select(driver.find_element(By.ID,"f_country"))
        sel.select_by_value(choose_country(sel))
        country = sel.first_selected_option.get_attribute("value")
    except:
        country = DEFAULT_COUNTRY_CODE

    # Attempt reCAPTCHA (manual may still be needed)
    try:
        driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR,"iframe[title='reCAPTCHA']"))
        driver.find_element(By.ID,"recaptcha-anchor").click()
        driver.switch_to.default_content()
    except: pass

    # Click Next
    try:
        next_btn = driver.find_element(By.ID,"_qf_page-0_next-0")
        if next_btn.is_enabled(): next_btn.click()
    except: st.info("Solve reCAPTCHA manually in Chrome before clicking 'Next'.")

    return {"full_name": full_name, "username": username, "email": email, "password": password, "country": country, "driver": driver}

# ---------------- STREAMLIT ----------------
def runAccGen():
    st.markdown("""
    <div class="header-card">
        <h1>4DinSingapore Acc Gen</h1>
        <p>Auto-fill your aMember signup form</p>
    </div>
    """, unsafe_allow_html=True)

    if "driver" not in st.session_state: st.session_state.driver=None

    if st.button("Generate Account") and st.session_state.driver is None:
        creds = run_browser()
        st.subheader("Generated Credentials")
        st.write(f"**Name:** {creds['full_name']}")
        st.write(f"**Email:** {creds['email']}")
        col1,col2 = st.columns([3,1]); col1.write(f"**Username:** {creds['username']}"); copy_text("Username", creds['username'])
        col1,col2 = st.columns([3,1]); col1.write(f"**Password:** {creds['password']}"); copy_text("Password", creds['password'])
        st.write(f"**Country:** {creds['country']}")
        st.markdown('<a href="https://4dinsingapore.com/amember/member/index" target="_blank">Go to aMember Member Index</a>', unsafe_allow_html=True)
        st.session_state.driver = creds["driver"]

    if st.session_state.driver:
        st.info("Chrome is detached and remains open. Solve reCAPTCHA manually if required.")
        if st.button("Close Browser"):
            try: st.session_state.driver.quit(); st.session_state.driver=None; st.success("Browser closed.")
            except Exception as e: st.error(f"Error closing browser: {e}")

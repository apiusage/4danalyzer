import random
import string
import streamlit as st
from st_copy import copy_button
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

# Optional Faker for nicer data
try:
    from faker import Faker
    faker = Faker()
except Exception:
    faker = None

# ---------------- CONFIG ----------------
PAGE_URL = "https://4dinsingapore.com/amember/signup"
HEADLESS = False  # Keep Chrome visible
IMPLICIT_WAIT = 6
RANDOMIZE_COUNTRY = True
DEFAULT_COUNTRY_CODE = "SG"
# ----------------------------------------

def copyable_text(label, text):
    copy_button(text, tooltip=f"Copy {label}", copied_label="Copied!", icon="st")

def runAccGen():
    """
    Full Streamlit + Selenium account generator.
    Call this function to launch the UI and handle account creation.
    """
    # ---------------- Streamlit UI Banner ----------------
    st.markdown(
        """
        <div style="
            background: linear-gradient(90deg,#5b6278,#464e5f);
            padding:10px 15px;
            border-radius:12px;
            text-align:center;
            box-shadow:0 3px 8px rgba(0,0,0,0.2);
            margin-bottom:15px;
        ">
            <h1 style="
                color:white;
                font-family:Arial,sans-serif;
                margin:0;
                font-size:1.8em;
                line-height:1.2;
                text-shadow:1px 1px 2px rgba(0,0,0,0.3);
            ">4DinSingapore Acc Gen</h1>
            <p style="color:#d1d5db;margin:3px 0 0 0;font-size:0.95em;">
            Auto-fill your aMember signup form</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Initialize session state for driver
    if "driver" not in st.session_state:
        st.session_state.driver = None

    # ---------------- Helper functions ----------------
    def random_username(min_length=6, max_length=8):
        words = ["silver","monkey","dragon","shadow","forest","candle",
                 "rocket","orange","tiger","purple","pencil","planet",
                 "green","stone","magic","cloud","flame"]
        base = faker.word() if faker else random.choice(words)
        base = base.lower()
        if len(base) < min_length:
            base += "".join(random.choice(string.ascii_lowercase) for _ in range(min_length-len(base)))
        if len(base) > max_length:
            base = base[:max_length]
        digits = "".join(random.choice(string.digits) for _ in range(random.choice([2,3])))
        return base + digits

    def random_email(name_hint=None):
        if faker:
            return faker.email()
        name = (name_hint or "user") + str(random.randint(100,999))
        domains = ["outlook.com","mailinator.com","gmail.com"]
        return f"{name}@{random.choice(domains)}"

    def random_name():
        if faker:
            return faker.name()
        first = random.choice(["Alex","Sam","Jamie","Taylor","Chris","Jordan","Morgan"])
        last = random.choice(["Lee","Tan","Ng","Lim","Wong","Smith","Chen"])
        return f"{first} {last}"

    def choose_country_value(select_elem, randomize=True, default_code="SG"):
        options = [opt.get_attribute("value") for opt in select_elem.options if opt.get_attribute("value")]
        if not options:
            return default_code
        if randomize:
            return random.choice(options)
        return default_code if default_code in options else options[0]

    # ---------------- Selenium automation ----------------
    def run_browser():
        options = webdriver.ChromeOptions()
        if HEADLESS:
            options.add_argument("--headless=new")
        else:
            options.add_argument("--start-maximized")
        options.add_experimental_option("detach", True)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--remote-allow-origins=*")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(IMPLICIT_WAIT)
        st.session_state.driver = driver

        driver.get(PAGE_URL)
        wait = WebDriverWait(driver, 12)

        # Select product
        try:
            radio = wait.until(EC.element_to_be_clickable((By.ID, "product-3-3")))
            driver.execute_script("arguments[0].scrollIntoView(true);", radio)
            radio.click()
        except Exception:
            radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio'][name^='product_id_page-0']")
            if radios:
                radios[0].click()

        # Generate credentials
        full_name = random_name()
        username = random_username()
        email = random_email(name_hint=username)
        password = "111111"

        # Fill form
        driver.find_element(By.NAME, "_name").send_keys(full_name)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "login").send_keys(username)
        driver.find_element(By.NAME, "pass").send_keys(password)

        # Select country
        try:
            select_el = Select(driver.find_element(By.ID, "f_country"))
            chosen_value = choose_country_value(select_el, randomize=RANDOMIZE_COUNTRY)
            select_el.select_by_value(chosen_value)
            country_used = chosen_value
        except Exception:
            country_used = DEFAULT_COUNTRY_CODE

        # Handle reCAPTCHA manually
        try:
            recaptcha_iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='reCAPTCHA']")))
            driver.switch_to.frame(recaptcha_iframe)
            checkbox = wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor")))
            checkbox.click()
            st.info("Solve reCAPTCHA manually in Chrome.")
            driver.switch_to.default_content()
        except Exception as e:
            st.warning(f"Cannot click reCAPTCHA automatically: {e}")

        return {
            "full_name": full_name,
            "username": username,
            "email": email,
            "password": password,
            "country": country_used,
            "driver": driver
        }

    # ---------------- Buttons ----------------
    if st.button("Generate Account") and st.session_state.driver is None:
        creds = run_browser()
        # Show credentials
        st.subheader("Generated Credentials")
        st.write(f"**Name:** {creds['full_name']}")
        st.write(f"**Email:** {creds['email']}")
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"**Username:** {creds['username']}")
        with col2:
            copyable_text("Username", creds['username'])
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"**Password:** {creds['password']}")
        with col2:
            copyable_text("Password", creds['password'])
        st.write(f"**Country:** {creds['country']}")
        st.markdown(
            f'<a href="https://4dinsingapore.com/amember/member/index" target="_blank">Go to aMember Member Index</a>',
            unsafe_allow_html=True
        )

    if st.session_state.driver:
        st.info("Chrome is detached and remains open. Solve reCAPTCHA manually.")
        if st.button("Close Browser"):
            try:
                st.session_state.driver.quit()
                st.session_state.driver = None
                st.success("Browser closed.")
            except Exception as e:
                st.error(f"Error closing browser: {e}")
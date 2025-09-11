import time
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

# Optional: nicer fake data; fallback if Faker not installed
try:
    from faker import Faker
    faker = Faker()
except Exception:
    faker = None

# ----- CONFIG -----
PAGE_URL = "https://4dinsingapore.com/amember/signup"
HEADLESS = False
IMPLICIT_WAIT = 6
RANDOMIZE_COUNTRY = True
DEFAULT_COUNTRY_CODE = "SG"
# -------------------

def random_username(min_length=6, max_length=8):
    words = [
        "silver", "monkey", "dragon", "shadow", "forest", "candle",
        "rocket", "orange", "tiger", "purple", "pencil", "planet",
        "green", "stone", "magic", "cloud", "flame"
    ]
    base = faker.word() if faker else random.choice(words)
    base = base.lower()
    if len(base) < min_length:
        base += ''.join(random.choice(string.ascii_lowercase) for _ in range(min_length - len(base)))
    if len(base) > max_length:
        base = base[:max_length]
    digits = ''.join(random.choice(string.digits) for _ in range(random.choice([2, 3])))
    return base + digits

def random_email(name_hint=None):
    if faker:
        return faker.email()
    name = (name_hint or "user") + str(random.randint(100,999))
    domains = ["outlook.com", "mailinator.com", "gmail.com"]
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

def copyable_text(label, text):
    copy_button(
        text,
        tooltip=f"Copy {label}",
        copied_label="Copied!",
        icon="st",
    )

def run_script():
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(IMPLICIT_WAIT)

    try:
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

        # Generate random values
        full_name = random_name()
        username = random_username()
        email = random_email(name_hint=username)
        password = "111111"

        # Fill inputs
        driver.find_element(By.NAME, "_name").send_keys(full_name)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "login").send_keys(username)
        driver.find_element(By.NAME, "pass").send_keys(password)

        try:
            select_el = Select(driver.find_element(By.ID, "f_country"))
            chosen_value = choose_country_value(select_el, randomize=RANDOMIZE_COUNTRY)
            select_el.select_by_value(chosen_value)
            country_used = chosen_value
        except Exception:
            country_used = DEFAULT_COUNTRY_CODE

        # Show credentials on Streamlit
        st.subheader("Generated Credentials")
        st.write(f"**Name:** {full_name}")
        st.write(f"**Email:** {email}")
        # Username row
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**Username:** {username}")
        with col2:
            copyable_text("Username", username)

        # Password row
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**Password:** {password}")
        with col2:
            copyable_text("Password", password)
        st.write(f"**Country:** {country_used}")

        # Define the URL for the aMember member index page
        member_index_url = "https://4dinsingapore.com/amember/member/index"

        # Create a clickable link using Markdown with HTML
        st.markdown(f'<a href="{member_index_url}" target="_blank">Go to aMember Member Index</a>',
                    unsafe_allow_html=True)

        # Click captcha checkbox
        try:
            recaptcha_iframe = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='reCAPTCHA']"))
            )
            driver.switch_to.frame(recaptcha_iframe)
            checkbox = wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor")))
            checkbox.click()
            st.info("Clicked reCAPTCHA checkbox. Please solve the challenge manually in the browser.")
            time.sleep(15)
        except Exception as e:
            st.warning(f"Could not click reCAPTCHA automatically: {e}")
        finally:
            driver.switch_to.default_content()

    finally:
        driver.quit()

def runAccGen():
    # Compact, stylish title banner
    st.markdown(
        """
        <div style="
            background: linear-gradient(90deg, #5b6278, #464e5f);
            padding: 10px 15px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 3px 8px rgba(0,0,0,0.2);
            margin-bottom: 15px;
            transition: all 0.3s ease;
        " onmouseover="this.style.boxShadow='0 6px 16px rgba(0,0,0,0.3)';" onmouseout="this.style.boxShadow='0 3px 8px rgba(0,0,0,0.2)';">
            <h1 style="
                color: white;
                font-family: 'Arial', sans-serif;
                margin: 0;
                font-size: 1.8em;
                line-height: 1.2;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            ">4DinSingapore Acc Gen</h1>
            <p style="
                color: #d1d5db;
                margin: 3px 0 0 0;
                font-size: 0.95em;
            ">Auto-fill your aMember signup form</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Run Autofill"):
        run_script()

# Run Streamlit app
if __name__ == "__main__":
    runAccGen()

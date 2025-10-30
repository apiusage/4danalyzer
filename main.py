import streamlit as st
from pathlib import Path
from PIL import Image
from setAnalysis import run_setAnalysis
from setHistory import run_setHistory
from streamlit_option_menu import option_menu
from winningCalculator import run_WinningCalculator
from sg4daccgen import runAccGen

st.set_page_config(
    page_title="4D Analyzer",
    page_icon=Image.open("logo.png"),
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown(f"<style>{Path('style.css').read_text()}</style>", unsafe_allow_html=True)

choice = option_menu(
    "4D Analyzer",
    ["Set History", "In-Depth Analysis", "Winning Calculator", "4DinSG", "About"],
    icons=['house-heart-fill', 'graph-up', 'calculator', 'bi bi-person-circle', 'question-circle'],
    orientation="horizontal",
    menu_icon="dice-4-fill",
    default_index=0,
)

if choice == "Set History":
    run_setHistory()
elif choice == "In-Depth Analysis":
    run_setAnalysis()
elif choice == "Winning Calculator":
    run_WinningCalculator()
elif choice == "4DinSG":
    runAccGen()
else:
    for title, text in [
        ("About", "A web application to analyze past 4D winning numbers."),
        ("Technologies Utilized", "Python, Streamlit, BeautifulSoup, Pandas, Requests"),
        ("Responsible Gambling", "__We are not responsible for any of your losses.__\nPlease leave the website if you are under 18 years old."),
        ("Legal", "You are responsible for any abuse or misuse of this tool."),
        ("Limitations", "We will not be held accountable for any damages that will arise with the use of this 4D analysis tool."),
        ("Terms", "By accessing this website, you are responsible for the agreement with any applicable local laws.")
    ]:
        st.info(f"__{title}__")
        st.write(text)
    st.balloons()
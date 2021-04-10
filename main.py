import streamlit as st 
import streamlit.components.v1 as stc
from PIL import Image
from setAnalysis import run_setAnalysis
from resultAnalysis import run_resultAnalysis
from digitAnalysis import run_digitAnalysis
from setHistory import run_setHistory
from scraping import run_scraping
 
img = Image.open("logo.png")
PAGE_CONFIG = {"page_title": "4D Analyzer", "page_icon":img, "layout":"centered", "initial_sidebar_state": "expanded" }
st.set_page_config(**PAGE_CONFIG)

LOGO_BANNER = """
    <div style="background-color:#6a0575;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;"> 4D Analyzer </h1>
    </div>
    """

def main():
    stc.html(LOGO_BANNER)

    menu = ["Home", "Set Analysis", "Result Analysis", "Digit Analysis", "Set History", "Run Scraping", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
    elif choice == "Set Analysis":
        run_setAnalysis()
    elif choice == "Result Analysis":
        run_resultAnalysis()
    elif choice == "Digit Analysis":
        run_digitAnalysis()   
    elif choice == "Set History":
        run_setHistory()   
    elif choice == "Run Scraping":
        run_scraping()  
    else:
        st.subheader("About")

if __name__ == '__main__':
    main()
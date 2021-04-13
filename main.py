import streamlit as st 
import streamlit.components.v1 as stc
from PIL import Image
from setAnalysis import run_setAnalysis
from resultAnalysis import run_resultAnalysis
from digitAnalysis import run_digitAnalysis
from setHistory import run_setHistory
from scraping import run_scraping
import streamlit.components.v1 as stc 
 
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
        stc.iframe("https://www.singaporepools.com.sg/en/product/pages/4d_results.aspx",
	    height=700,width=300,
	    scrolling=True
	    )
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
        st.info("__About__")
        st.write("A web application to analyze past 4D winning numbers.")
        st.info("__Techology Utilized__")
        st.write("Python, Streamlit, BeautifulSoup, Pandas, Requests")
        st.info("__Responsible Gambling__")
        st.write("__We are not responsible for any of your losses.__")
        st.write("Please leave the website if you are under 18 years old.")
        st.info("__Legal__")
        st.write("You are responsible for any abuse or misuse of this tool.")
        st.info("__Limitations__")
        st.write("We will not be hold accountable for any damages that will\
                 arise with the use of this 4D analysis tool.")
        st.info("__Terms__")
        st.write("By accessing this website, you are responsible for \
                 the agreement with any applicable local laws.")
        st.balloons()

if __name__ == '__main__':
    main()
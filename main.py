import streamlit as st 
import streamlit.components.v1 as stc
from PIL import Image
from setAnalysis import run_setAnalysis
from digitAnalysis import run_digitAnalysis
from setHistory import run_setHistory
from scraping import run_scraping
import streamlit.components.v1 as stc
from streamlit_option_menu import option_menu
 
img = Image.open("logo.png")
PAGE_CONFIG = {"page_title": "4D Analyzer", "page_icon":img, "layout":"centered", "initial_sidebar_state": "expanded" }
st.set_page_config(**PAGE_CONFIG)

LOGO_BANNER = """
    <div style="background-color:#6a0575;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;"> 4D Analyzer </h1>
    </div>
    """

def main():
    choice = optionMenu()

    if choice == "Home":
        stc.iframe("https://www.singaporepools.com.sg/en/product/pages/4d_results.aspx",
	    height=700,width=300,
	    scrolling=True
	    )
    elif choice == "Set Analysis":
        run_setAnalysis()
    elif choice == "Digit Analysis":
        run_digitAnalysis()
    elif choice == "Set History":
        run_setHistory()   
    elif choice == "Run Scraping":
        run_scraping()     
    else:
        st.info("__About__")
        st.write("A web application to analyze past 4D winning numbers.")
        st.info("__Technologies Utilized__")
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

def optionMenu():
    option = option_menu("4D Analyzer",
                         ["Home", "Set Analysis", "Digit Analysis", "Set History", "Run Scraping", "About"],
                         icons=['house-heart-fill', 'graph-up', 'graph-up-arrow', 'wallet', 'card-checklist',
                                'question-circle'],
                         orientation="horizontal", menu_icon="dice-4-fill", default_index=0,
                         styles={
                             "container": {"padding": "5!important", "background-color": "#fafafa"},
                             "icon": {"color": "orange", "font-size": "16px"},
                             "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px",
                                          "--hover-color": "#eee"},
                             "nav-link-selected": {"background-color": "#02ab21"},
                         }
                         )
    return option

if __name__ == '__main__':
    main()


from PIL import Image
from setAnalysis import run_setAnalysis
from setHistory import *
from streamlit_option_menu import option_menu
from winningCalculator import *
from sg4daccgen import *

img = Image.open("logo.png")
PAGE_CONFIG = {
    "page_title": "4D Analyzer",
    "page_icon": img,
    "layout": "centered",
    "initial_sidebar_state": "expanded"
}
st.set_page_config(**PAGE_CONFIG)

LOGO_BANNER = """
    <div style="background-color:#6a0575;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;"> 4D Analyzer </h1>
    </div>
    """

def main():
    choice = optionMenu()

    if choice == "Set History":
         run_setHistory()
    elif choice == "In-Depth Analysis":
        run_setAnalysis()
    elif choice == "Winning Calculator":
        run_WinningCalculator()
    elif choice == "4DinSG":
        runAccGen()
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
        st.write("We will not be held accountable for any damages that will \
                 arise with the use of this 4D analysis tool.")
        st.info("__Terms__")
        st.write("By accessing this website, you are responsible for \
                 the agreement with any applicable local laws.")
        st.balloons()

def optionMenu():
    option = option_menu("4D Analyzer",
                         ["Set History", "In-Depth Analysis", "Winning Calculator", "4DinSG", "About"],
                         icons=['house-heart-fill', 'graph-up', 'calculator', 'bi bi-person-circle', 'question-circle'],
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

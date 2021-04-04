import streamlit as st 
from PIL import Image
from setAnalysis import run_setAnalysis
from resultAnalysis import run_resultAnalysis
from digitAnalysis import run_digitAnalysis
from setHistory import run_setHistory

img = Image.open("logo.png")
PAGE_CONFIG = {"page_title": "4D Analyzer", "page_icon":img, "layout":"centered", "initial_sidebar_state": "expanded" }
st.set_page_config(**PAGE_CONFIG)

def main():
    st.title("4D Analyzer")

    menu = ["Home", "Set Analysis", "Result Analysis", "Digit Analysis", "Set History", "About"]
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
    else:
        st.subheader("About")

if __name__ == '__main__':
    main()
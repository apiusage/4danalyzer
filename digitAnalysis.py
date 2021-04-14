import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np

def run_digitAnalysis():
    st.info("__4D Digit Analysis__")

    numberList = st.text_area("Enter winning numbers list: ", height=150)
    numberList = filterList(numberList)
    digitAnalysis(numberList)


def digitAnalysis(numberList):
    digit1Data, digit2Data, digit3Data, digit4Data, RoundNo = [], [], [], [], []
    i = 0
    if numberList is not None:
        for num in numberList:
            digit1Data.insert(0, num[0:1])
            digit2Data.insert(0, num[1:2])
            digit3Data.insert(0, num[2:3])
            digit4Data.insert(0, num[3:4])

            RoundNo.append(i)
            i += 1

    st.info("Digit 1")
    digit1DF = pd.DataFrame({
        'Round': 9,
        'Digit 1': digit1Data
    })
    st.line_chart(digit1DF, use_container_width=True)

    st.info("Digit 2")
    digit2DF = pd.DataFrame({
        'Round': 9,
        'Digit 2': digit2Data
    })
    st.line_chart(digit2DF, use_container_width=True)

    st.info("Digit 3")
    digit3DF = pd.DataFrame({
        'Round': 9,
        'Digit 3': digit3Data
    })
    st.line_chart(digit3DF, use_container_width=True)

    st.info("Digit 4")
    digit4DF = pd.DataFrame({
        'Round': 9,
        'Digit 4': digit4Data
    })
    st.line_chart(digit4DF, use_container_width=True)


 # Filter 4 digits
def filterList(numberList):
    numberClean = []
    if numberList is not None:
        numberSplit = numberList.split()

    for num in numberSplit:
        if num.isnumeric() and len(num) == 4:
            numberClean.append(num)

    return numberClean   
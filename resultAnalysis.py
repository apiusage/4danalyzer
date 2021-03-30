import streamlit as st
import pandas as pd
from collections import Counter
import plotly.express as px

def run_resultAnalysis():
    st.subheader("4D Pattern Analysis")

    numberList = st.text_area("Enter winning numbers list", height=150)
    numberList = filterList(numberList)
    getNumPattern(numberList)

def getNumPattern(numberList):
    patternDict = {"AAAA": [], "AAAB": [], "AABB": [], "AABC": [], "ABCD": []}
    if numberList is not None:
        while len(numberList) > 22:
            AAAAfreq, AAABfreq, AABBfreq, AABCfreq, ABCDfreq = 0, 0, 0, 0, 0
            for num in numberList[:23]:
                    if isAAAA(num):
                        AAAAfreq += 1
                    if isAAAB(num):
                        AAABfreq += 1
                    if isAABB(num):
                        AABBfreq += 1
                    if isAABC(num):
                        AABCfreq += 1
                    if isABCD(num):
                        ABCDfreq += 1

            patternDict["AAAA"].insert(0, AAAAfreq)
            patternDict["AAAB"].insert(0, AAABfreq)
            patternDict["AABB"].insert(0, AABBfreq)
            patternDict["AABC"].insert(0, AABCfreq)
            patternDict["ABCD"].insert(0, ABCDfreq)
            del numberList[:23]

    # Pattern data frame
    patternDF = pd.DataFrame(data=patternDict)
    st.dataframe(patternDF)
    st.line_chart(patternDF, use_container_width=True)
    
    # Display Total Freq
    patternDF = patternDF.sum(axis=0)
    data = patternDF.to_dict()
    sumData = pd.DataFrame(data, index=[0])
    st.dataframe(sumData)

def isAAAA(number):
    uniqueSet = {number[0:1], number[1:2], number[2:3], number[3:4]}
    return len(uniqueSet) == 1 if True else False


def isAAAB(number):
    uniqueSet = [number[0:1], number[1:2], number[2:3], number[3:4]]
    return 3 in Counter(uniqueSet).values() if True else False


def isAABB(number):
    uniqueSet = [number[0:1], number[1:2], number[2:3], number[3:4]]
    return (
        list(Counter(uniqueSet).values())[0] == 2
        and list(Counter(uniqueSet).values())[1] == 2
        if True
        else False)

def isAABC(number):
    uniqueSet = {number[0:1], number[1:2], number[2:3], number[3:4]}
    return len(uniqueSet) == 3 if True else False


def isABCD(number):
    uniqueSet = {number[0:1], number[1:2], number[2:3], number[3:4]}
    return len(uniqueSet) == 4 if True else False

# Filter 4 digits
def filterList(numberList):
    numberClean = []
    if numberList is not None:
        numberSplit = numberList.split()

    for num in numberSplit:
        if num.isnumeric() and len(num) == 4:
            numberClean.append(num)

    return numberClean


def displayChart(patternDF):
    pieChart = px.pie(patternDF, values="Count", names="Pattern", title="4D Pattern")
    st.plotly_chart(pieChart, use_container_width=True)

    barChart = px.bar(patternDF, x="Pattern", y="Count")
    st.plotly_chart(barChart, use_container_width=True)
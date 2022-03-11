import streamlit as st
import pandas as pd
from collections import Counter
import plotly.express as px

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

    # Display Total Freq
    st.write("__*For every 23 numbers in the list, it will treat it as 1 round.*__")
    allPatternDF = pd.DataFrame(data=patternDict) 
    st.dataframe(allPatternDF)

    # Display sum pattern
    sum_column = allPatternDF.sum(axis=0)
    transposedSumDF = sum_column.T
    st.dataframe(transposedSumDF)

    # Pattern data frame
    st.info("ABCD")
    abcdDF = pd.DataFrame(data=patternDict["ABCD"])
    st.dataframe(abcdDF)
    st.line_chart(abcdDF, use_container_width=True)

    st.info("AABC")
    aabcDF = pd.DataFrame(data=patternDict["AABC"])
    st.dataframe(aabcDF)
    st.line_chart(aabcDF, use_container_width=True)

    st.info("AAAB")
    aaabDF = pd.DataFrame(data=patternDict["AAAB"])
    st.dataframe(aaabDF)
    st.line_chart(aaabDF, use_container_width=True)

    st.info("AABB")
    aabbDF = pd.DataFrame(data=patternDict["AABB"])
    st.dataframe(aabbDF)
    st.line_chart(aabbDF, use_container_width=True)

    st.info("AAAA")
    aaaaDF = pd.DataFrame(data=patternDict["AAAA"])
    st.dataframe(aaaaDF)
    st.line_chart(aaaaDF, use_container_width=True)

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
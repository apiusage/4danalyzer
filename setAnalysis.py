import streamlit as st 
import pandas as pd 

def run_setAnalysis():
    st.subheader("4D Sets Data Analysis")
    df = pd.read_csv("data/4D Sets.csv")
    # add zero leadings to 4D numbers
    df['Number'] = df['Number'].apply(lambda num: '{0:0>4}'.format(num))

    numberList = st.text_area("Enter numbers", height=150)
    st.table(filterList(df, numberList))

    st.dataframe(df)

# Filter 4 digits
def filterList(df, numberList):
    numberClean = []
    if numberList is not None:
       numberSplit = numberList.split()

       for num in numberSplit: 
           if (num.isnumeric() and len(num) == 4):
             numberClean.append(num)

       boolean_series = df.Number.isin(numberClean)
       filtered_df = df[boolean_series]

       return filtered_df


import streamlit as st 
import pandas as pd 

def run_setAnalysis():
    st.info("__4D Sets Freq Analysis__")

    df = pd.read_csv("data/4D Sets.csv")
    # add zero leadings to 4D numbers
    df['Number'] = df['Number'].apply(lambda num: '{0:0>4}'.format(num))
    df['Digit Sum'] = df['Number'].apply(sum_digits)

    numberList = st.text_area("Enter set numbers: ", height=150)
    st.table(filterList(df, numberList))

    st.dataframe(df)

# Filter 4 digits
def filterList(df, numberList):
    numberClean = []
    if numberList is not None:
       numberSplit = numberList.split()

       for num in numberSplit: 
           if (num.isnumeric() and len(num) == 4):
             tempArray = [num[0:1], num[1:2], num[2:3], num[3:4]]
             num = sorted(tempArray)
             numberClean.append(''.join(num))

       boolean_series = df.Number.isin(numberClean)
       filtered_df = df[boolean_series]

       return filtered_df

def sum_digits(n):
    n = int(n)
    s = 0
    while n:
        s += n % 10
        n //= 10
    return s

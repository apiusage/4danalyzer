import streamlit as st 
import pandas as pd 
import streamlit.components.v1 as stc 

def run_setAnalysis():
    st.subheader("4D Sets Data Analysis")
    stc.iframe("https://www.singaporepools.com.sg/en/product/pages/4d_results.aspx",
		height=700,width=300,
		scrolling=True
		)

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
             tempArray = [num[0:1], num[1:2], num[2:3], num[3:4]]
             num = sorted(tempArray)
             numberClean.append(''.join(num))

       boolean_series = df.Number.isin(numberClean)
       filtered_df = df[boolean_series]

       return filtered_df


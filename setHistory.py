import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import base64
import itertools

def run_setHistory():
    numberList = st.text_area("Enter winning numbers list", height=150)
    numberList = filterList(numberList)

    col1, col2 = st.beta_columns(2)
    showGraph = col1.checkbox('Show all graphs')
    genPermutation = col2.checkbox('Generate Permutations')

    run_Scraping(numberList, showGraph, genPermutation)

def run_Scraping(numberList, showGraph, genPermutation):
    try:
        url = 'https://www.singaporepools.com.sg/_layouts/15/FourD/FourDCommon.aspx/Get4DNumberCheckResultsJSON'
        headers = {
            'Host': 'www.singaporepools.com.sg',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://www.singaporepools.com.sg/en/product/Pages/4d_cpwn.aspx',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Length': '76'
        }

        # Convert milliseconds to local time
        def getDateFromDrawDate(x):
            x = x.replace('/Date(', '')
            x = int(x.replace(')/', ''))
            return datetime.fromtimestamp(x/1000).strftime('%Y-%m-%d')

        def GetResultsJson(num):
            data = json.dumps({"numbers": [str(num).zfill(4)], "checkCombinations": "true", "sortTypeInteger": "1"})
            r = requests.post(url=url, data=data, headers=headers)
            ResultsData = json.loads(r.json().get('d'))[0].get('Prizes')
            Results_df = pd.DataFrame.from_dict(ResultsData)  # dict to DF
            Results_df["DrawDate"] = Results_df["DrawDate"].apply(getDateFromDrawDate, 1)
            Results_df["Digit"] = str(num).zfill(4)

            # Line chart
            dateList = Results_df['DrawDate'].values.tolist()
            prizeCodeList = Results_df['PrizeCode'].values.tolist()
            lineChartDF = pd.DataFrame({
                'date': dateList,
                'prizeCode': prizeCodeList
            })
            lineChartDF = lineChartDF.set_index('date')
            if showGraph:
                st.success(num)
                st.line_chart(lineChartDF, use_container_width=True)

            return Results_df

        for n in numberList:
            ResultsAll = pd.DataFrame()
            ResultsData = None
            
            if genPermutation:
                array = [''.join(i) for i in itertools.permutations(n, 4)]
                array = remove_duplicates(array)
                array = sorted(array)
            
            while ResultsData is None:
                try:
                    if genPermutation:
                        for num in array:
                            ResultsData = GetResultsJson(num)
                            ResultsAll = ResultsAll.append(ResultsData)
                    else: 
                        ResultsData = GetResultsJson(n)
                        ResultsAll = ResultsAll.append(ResultsData)
                except:
                    pass

            st.success("Set: " + n)
            ResultsAll = ResultsAll.reset_index()
            ResultsAll = ResultsAll.sort_index(ascending=False)
            st.dataframe(ResultsAll)
            dateList = ResultsAll['DrawDate'].values.tolist()
            prizeCodeList = ResultsAll['PrizeCode'].values.tolist()
            lineChartDF = pd.DataFrame({
            'date': dateList,
            'prizeCode': prizeCodeList
            })
            lineChartDF = lineChartDF.set_index('date')
            lineChartDF.sort_values(by=['date'], inplace=True, ascending=False)
            st.line_chart(lineChartDF.head(15), use_container_width=True)
                
            
        if st.button('Download 4D Data as CSV'):
            tmp_download_link = download_link(ResultsAll, '4D_Data.csv', 'Download Data as CSV')
            st.markdown(tmp_download_link, unsafe_allow_html=True)
    except:
        pass

# Filter 4 digits
def filterList(numberList):
    numberClean = []
    if numberList is not None:
        numberSplit = numberList.split()

    for num in numberSplit:
        if num.isnumeric() and len(num) == 4:
            numberClean.append(num)

    return numberClean

def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def remove_duplicates(l):
    return list(set(l))




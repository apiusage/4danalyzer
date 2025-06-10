import streamlit as st
from bs4 import BeautifulSoup
from lxml import etree
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import base64
import itertools
import xlsxwriter
from st_copy_to_clipboard import st_copy_to_clipboard
from scrape4D2U import get_from_latest_drawno

def run_setHistory():
    numberList = st.text_area("Enter direct / set numbers: ", height=150)
    numberList = filterList(numberList)

    col1, col2, col3 = st.columns(3)
    genPermutation = col1.checkbox('Generate Permutations')

    if st.button('Scrape Last Round'):
        numberList = scrapeLastRound()

    run_Scraping(numberList, genPermutation)

def run_Scraping(numberList, genPermutation):
    try:
        url = 'https://www.singaporepools.com.sg/_layouts/15/FourD/FourDCommon.aspx/Get4DNumberCheckResultsJSON'
        headers = {
            'Host': 'www.singaporepools.com.sg',
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }

        def getDateFromDrawDate(x):
            x = x.replace('/Date(', '').replace(')/', '')
            local_time = datetime.fromtimestamp(int(x) / 1000)
            local_time += timedelta(days=1)
            return local_time.strftime('%Y-%m-%d')

        def GetResultsJson(num):
            data = json.dumps({"numbers": [str(num).zfill(4)], "checkCombinations": "true", "sortTypeInteger": "1"})
            r = requests.post(url=url, data=data, headers=headers)
            ResultsData = json.loads(r.json().get('d'))[0].get('Prizes')
            Results_df = pd.DataFrame.from_dict(ResultsData)
            Results_df["DrawDate"] = Results_df["DrawDate"].apply(lambda x: pd.Series(getDateFromDrawDate(x), dtype="object"))
            Results_df["Digit"] = str(num).zfill(4)
            return Results_df

        def getPermutation(n):
            array = [''.join(i) for i in itertools.permutations(n, 4)]
            array = remove_duplicates(array)
            return sorted(array)

        def showGraph(SetResultData):
            with st.expander(label=str(num)):
                lineChartDF = pd.DataFrame({
                    'date': SetResultData['DrawDate'].values.tolist(),
                    'prizeCode': SetResultData['PrizeCode'].values.tolist()
                }).set_index('date')
                st.line_chart(lineChartDF, use_container_width=True)
                st.dataframe(SetResultData['PrizeCode'].value_counts().sort_index(ascending=True))

        for n in numberList:
            ResultsAll = pd.DataFrame()
            try:
                if genPermutation:
                    array = getPermutation(n)
                    for num in array:
                        SetResultData = None
                        while SetResultData is None:
                            SetResultData = GetResultsJson(num)
                        showGraph(SetResultData)
                        ResultsAll = pd.concat([ResultsAll, SetResultData], ignore_index=True, axis=0)
                else:
                    SetResultData = None
                    while SetResultData is None:
                        SetResultData = GetResultsJson(n)
                    st.dataframe(SetResultData.sort_values(by=['DrawDate'], ascending=False), width=400)
                    ResultsAll = SetResultData.copy()
            except:
                pass

            with st.expander(label="Set: " + n + " / Total Freq: " + str(ResultsAll.shape[0]), expanded=True):
                lineChartDF = pd.DataFrame({
                    'date': ResultsAll['DrawDate'].values.tolist(),
                    'prizeCode': ResultsAll['PrizeCode'].values.tolist()
                }).set_index('date')
                lineChartDF.sort_values(by=['date'], inplace=True, ascending=False)
                st.line_chart(lineChartDF.head(15), use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(ResultsAll.sort_values(by=['DrawDate'], ascending=False))
                with col2:
                    column_to_copy = ResultsAll.sort_values(by="DrawDate")['Digit'].to_string(index=False, header=False)
                    st_copy_to_clipboard(column_to_copy)

                st.dataframe(ResultsAll['PrizeCode'].value_counts().sort_index(ascending=True))
                st.dataframe(ResultsAll['Digit'].value_counts())

                # New Enhanced Frequency Table with "From Latest DrawNo"
                with st.spinner("Fetching 'From Latest DrawNo' values..."):
                        freq_df = ResultsAll['Digit'].value_counts().reset_index()
                        freq_df.columns = ['Digit', 'Frequency']
                        freq_df['From Latest DrawNo'] = freq_df['Digit'].apply(get_from_latest_drawno)
                        st.dataframe(freq_df)

                tmp_download_link = download_link(ResultsAll, '4D_Data.csv', '** ⬇️ Download as CSV file **')
                st.markdown(tmp_download_link, unsafe_allow_html=True)

        st.markdown("<div style='text-align:right'><a href='#top'>------- ↟ Go to top ↟ -------</a></div>", unsafe_allow_html=True)

    except:
        pass

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
    b64 = base64.b64encode(object_to_download.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def remove_duplicates(l):
    return list(set(l))

def scrapeLastRound():
    allResult = []
    start_url = ("http://www.singaporepools.com.sg/DataFileArchive/Lottery/Output/fourd_result_draw_list_en.html")
    HEADERS = ({'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US, en;q=0.5'})
    webpage = requests.get(start_url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "html.parser")
    dom = etree.HTML(str(soup))
    dates = dom.xpath("//select/option")
    for date in dates:
        url = "http://www.singaporepools.com.sg/en/4d/Pages/Results.aspx?" + date.xpath("@querystring")[0]
        drawPage = requests.get(url, headers=HEADERS)
        if drawPage.ok:
            soup = BeautifulSoup(drawPage.content, "html.parser")
            dom = etree.HTML(str(soup))
            allResult.extend([
                dom.xpath('//td[@class="tdFirstPrize"]')[0].text,
                dom.xpath('//td[@class="tdSecondPrize"]')[0].text,
                dom.xpath('//td[@class="tdThirdPrize"]')[0].text
            ])
            allResult.extend(dom.xpath("//tbody[@class='tbodyStarterPrizes']//td/text()"))
            allResult.extend(dom.xpath("//tbody[@class='tbodyConsolationPrizes']//td/text()"))
        break
    return allResult

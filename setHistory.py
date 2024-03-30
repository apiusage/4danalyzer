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
             # Convert milliseconds to local time
             local_time = datetime.fromtimestamp(x / 1000)
             # Add one day to the local time
             local_time += timedelta(days=1)
             return local_time.strftime('%Y-%m-%d')

        def GetResultsJson(num):
            data = json.dumps({"numbers": [str(num).zfill(4)], "checkCombinations": "true", "sortTypeInteger": "1"})
            r = requests.post(url=url, data=data, headers=headers)
            ResultsData = json.loads(r.json().get('d'))[0].get('Prizes')
            Results_df = pd.DataFrame.from_dict(ResultsData)  # dict to DF
            Results_df["DrawDate"] = Results_df["DrawDate"].apply(lambda x: pd.Series(getDateFromDrawDate(x), dtype="object"))
            Results_df["Digit"] = str(num).zfill(4)
            return Results_df

        def getPermutation(n):
            array = [''.join(i) for i in itertools.permutations(n, 4)]
            array = remove_duplicates(array)
            array = sorted(array)

            return array

        def showGraph(SetResultData):
            with st.expander(label=str(num)):
                # Line chart
                dateList = SetResultData['DrawDate'].values.tolist()
                prizeCodeList = SetResultData['PrizeCode'].values.tolist()
                lineChartDF = pd.DataFrame({
                    'date': dateList,
                    'prizeCode': prizeCodeList
                })
                lineChartDF = lineChartDF.set_index('date')
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
            except:
                pass

        # Expander should be outside the loop
        with st.expander(label="Set: " + n + " / Total Freq: " + str(ResultsAll.shape[0]), expanded=True):  # rows
            dateList = ResultsAll['DrawDate'].values.tolist()
            prizeCodeList = ResultsAll['PrizeCode'].values.tolist()
            lineChartDF = pd.DataFrame({
                'date': dateList,
                'prizeCode': prizeCodeList
            })
            lineChartDF = lineChartDF.set_index('date')
            lineChartDF.sort_values(by=['date'], inplace=True, ascending=False)
            st.line_chart(lineChartDF.head(15), use_container_width=True)
            st.dataframe(ResultsAll.sort_values(by=['DrawDate'], ascending=False), width=400)
            st.dataframe(ResultsAll['PrizeCode'].value_counts().sort_index(ascending=True))
            st.dataframe(ResultsAll['Digit'].value_counts())

            tmp_download_link = download_link(ResultsAll, '4D_Data.csv', '** ⬇️ Download as CSV file **')
            st.markdown(tmp_download_link, unsafe_allow_html=True)

        st.markdown("<div style='text-align:right'><a href='#top'>------- ↟ Go to top ↟ -------</a></div>", unsafe_allow_html=True)

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


def scrapeLastRound():
    allResult = []
    start_url = ("http://www.singaporepools.com.sg/DataFileArchive/Lottery/Output/fourd_result_draw_list_en.html")

    HEADERS = ({'User-Agent':
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', \
                'Accept-Language': 'en-US, en;q=0.5'})

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
            fPrize = dom.xpath('//td[@class="tdFirstPrize"]')[0].text
            sPrize = dom.xpath('//td[@class="tdSecondPrize"]')[0].text
            tPrize = dom.xpath('//td[@class="tdThirdPrize"]')[0].text
            allResult.extend([fPrize, sPrize, tPrize])
            for number in dom.xpath("//tbody[@class='tbodyStarterPrizes']//td/text()"):
                allResult.extend([number])
            for number in dom.xpath("//tbody[@class='tbodyConsolationPrizes']//td/text()"):
                allResult.extend([number])
        break

    return allResult

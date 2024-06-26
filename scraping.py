# https://www.geeksforgeeks.org/how-to-use-xpath-with-beautifulsoup/

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree
import base64
import time
from io import BytesIO
from resultAnalysis import getNumPattern

timestr = time.strftime("%m-%d-%Y")

def run_scraping():
    st.info("__Ultimate 4D Scraper (Digit Sum / Pattern Analysis)__")
    st.write("Scrape past 1st, 2nd, 3rd winning prize numbers including all winning numbers.")

    start_url = ("http://www.singaporepools.com.sg/DataFileArchive/Lottery/Output/fourd_result_draw_list_en.html")

    HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
            'Accept-Language': 'en-US, en;q=0.5'})

    numOfRound = st.number_input("Number of rounds to scrape: ", 0)
    
    scrapeAll = st.checkbox('Scrape all') 
    if st.button('Scrape'):
        webpage = requests.get(start_url, headers=HEADERS)
        soup = BeautifulSoup(webpage.content, "html.parser")
        dom = etree.HTML(str(soup))

        dates = dom.xpath("//select/option")

        topPrizesDF = pd.DataFrame(columns=['1st Prize', '2nd Prize', '3rd Prize'])
        allResult = []
        my_bar = st.progress(0)
        current_count = 0
        digitSum = {"1st Prize": [], "2nd Prize": [], "3rd Prize": []}
        for date in dates:
            url = "http://www.singaporepools.com.sg/en/4d/Pages/Results.aspx?" + date.xpath("@querystring")[0]
            drawPage = requests.get(url, headers=HEADERS)
            if current_count == numOfRound and not scrapeAll:
                break
            if drawPage.ok:
                current_count += 1    
            soup = BeautifulSoup(drawPage.content, "html.parser")
            dom = etree.HTML(str(soup))

            fPrize = dom.xpath('//td[@class="tdFirstPrize"]')[0].text
            sPrize = dom.xpath('//td[@class="tdSecondPrize"]')[0].text
            tPrize = dom.xpath('//td[@class="tdThirdPrize"]')[0].text

            starters = []
            for number in dom.xpath("//tbody[@class='tbodyStarterPrizes']//td/text()") :
                starters.append(number)

            consolations = []
            for number in dom.xpath("//tbody[@class='tbodyConsolationPrizes']//td/text()") :
                consolations.append(number)  

            topPrizesDF = pd.concat([topPrizesDF, pd.DataFrame({'1st Prize': [fPrize], '2nd Prize': [sPrize], '3rd Prize': [tPrize]})], ignore_index=True)
            allResult.extend([fPrize, sPrize, tPrize])
            allResult.extend(starters)
            allResult.extend(consolations)
            
            current_percent = percentage(current_count, numOfRound)
            my_bar.progress(int(current_percent))

            digitSum["1st Prize"].insert(0, fPrize)
            digitSum["2nd Prize"].insert(0, sPrize)
            digitSum["3rd Prize"].insert(0, tPrize)

        st.balloons()
        allResultDF = pd.DataFrame(allResult, columns=['All Numbers'])
        finalDF = pd.concat([topPrizesDF, allResultDF], axis=1)
        st.dataframe(finalDF)
        st.markdown("### ** 📩 ⬇️ Download 4D file **")
        st.markdown(get_table_download_link(finalDF), unsafe_allow_html=True)

        with st.expander("Digit Sum"):
            topPrizesDF = pd.DataFrame(data=digitSum)
            topPrizesDF['1st Prize DS'] = topPrizesDF['1st Prize'].apply(sum_digits)
            topPrizesDF['2nd Prize DS'] = topPrizesDF['2nd Prize'].apply(sum_digits)
            topPrizesDF['3rd Prize DS'] = topPrizesDF['3rd Prize'].apply(sum_digits)
            reversed_df = topPrizesDF.iloc[::-1]
            st.dataframe(reversed_df)

            st.info("__1st Prize Digit Sum__")
            st.line_chart(topPrizesDF['1st Prize DS'], use_container_width=True)
            st.info("__2nd Prize Digit Sum__")
            st.line_chart(topPrizesDF['2nd Prize DS'], use_container_width=True)
            st.info("__3rd Prize Digit Sum__")
            st.line_chart(topPrizesDF['3rd Prize DS'], use_container_width=True)

        with st.expander("Pattern Analysis"):
            getNumPattern(allResult)


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=timestr, index=False)
    writer.close()
    processed_data = output.getvalue()
    return processed_data    

def get_table_download_link(df):
    filename = "{}_4D_Result.xlsx".format(timestr)
    val = to_excel(df)
    b64 = base64.b64encode(val) 
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">Download Excel file</a>' # decode b'abc' => abc

def percentage(part, whole):
  return 100 * float(part)/float(whole)

def sum_digits(n):
    n = int(n)
    s = 0
    while n:
        s += n % 10
        n //= 10
    return s

# https://www.geeksforgeeks.org/how-to-use-xpath-with-beautifulsoup/

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree
import base64
import time
from io import BytesIO

timestr = time.strftime("%m-%d-%Y")

def run_scraping():
    st.subheader("Ultimate 4D Scraper")

    start_url = ("http://www.singaporepools.com.sg/DataFileArchive/Lottery/Output/fourd_result_draw_list_en.html")

    HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
            'Accept-Language': 'en-US, en;q=0.5'})
  
    webpage = requests.get(start_url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "html.parser")
    dom = etree.HTML(str(soup))

    dates = dom.xpath("//select/option")

    topPrizesDF = pd.DataFrame(columns=['1st Prize', '2nd Prize', '3rd Prize'])
    allResult = []
    for date in dates:
        url = "http://www.singaporepools.com.sg/en/4d/Pages/Results.aspx?" + date.xpath("@querystring")[0]
        drawPage = requests.get(url, headers=HEADERS)
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

        topPrizesDF = topPrizesDF.append({'1st Prize': fPrize, '2nd Prize': sPrize, '3rd Prize': tPrize}, ignore_index=True)
        allResult.extend([fPrize, sPrize, tPrize])
        allResult.extend(starters)
        allResult.extend(consolations)
    
    allResultDF = pd.DataFrame (allResult, columns=['All Numbers'])
    finalDF = pd.concat([topPrizesDF, allResultDF], axis=1)
    st.dataframe(finalDF)
    st.markdown("### ** 📩 ⬇️ Download 4D file **")
    st.markdown(get_table_download_link(finalDF), unsafe_allow_html=True)    
    
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=timestr, index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data    

def get_table_download_link(df):
    filename = "{}_4D_Result.xlsx".format(timestr)
    val = to_excel(df)
    b64 = base64.b64encode(val) 
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">Download Excel file</a>' # decode b'abc' => abc

    
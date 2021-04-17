import streamlit as st 
import pandas as pd 
import requests
from bs4 import BeautifulSoup
from lxml import etree

def run_digitSum():
    st.info("__4D Digit Sum__")

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
        my_bar = st.progress(0)
        current_count = 0
        digitSum = {"1st Prize": [], "2nd Prize": [], "3rd Prize": []}
        for date in dates:
            url = "http://www.singaporepools.com.sg/en/4d/Pages/Results.aspx?" + date.xpath("@querystring")[0]
            drawPage = requests.get(url, headers=HEADERS)
            if current_count == numOfRound and not scrapeAll:
                break
            if (drawPage.ok):
                current_count += 1    
            soup = BeautifulSoup(drawPage.content, "html.parser")
            dom = etree.HTML(str(soup))

            fPrize = dom.xpath('//td[@class="tdFirstPrize"]')[0].text
            sPrize = dom.xpath('//td[@class="tdSecondPrize"]')[0].text
            tPrize = dom.xpath('//td[@class="tdThirdPrize"]')[0].text

            digitSum["1st Prize"].insert(0, fPrize)
            digitSum["2nd Prize"].insert(0, sPrize)
            digitSum["3rd Prize"].insert(0, tPrize)
            
            current_percent = percentage(current_count, len(dates))
            my_bar.progress(int(current_percent))

        st.balloons()
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



def percentage(part, whole):
  return 100 * float(part)/float(whole)        

def sum_digits(n):
    n = int(n)
    s = 0
    while n:
        s += n % 10
        n //= 10
    return s
  
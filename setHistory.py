import streamlit as st
from bs4 import BeautifulSoup
from lxml import etree
import requests
import json
from datetime import datetime, timezone, timedelta
import pandas as pd
import base64
import itertools
from st_copy_to_clipboard import st_copy_to_clipboard
from scrape4D2U import get_from_latest_drawno
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------------------------
# Main entry
# -------------------------
def run_setHistory():
    numberList = st.text_area("Enter direct / set numbers: ", height=150)
    numberList = filterList(numberList)

    col1, col2, col3 = st.columns(3)
    genPermutation = col1.checkbox('Generate Permutations')

    if st.button('Scrape Last Round'):
        numberList = scrapeLastRound()

    run_Scraping(numberList, genPermutation)

# -------------------------
# Scraping & Display
# -------------------------
def run_Scraping(numberList, genPermutation):
    try:
        URL = 'https://www.singaporepools.com.sg/_layouts/15/FourD/FourDCommon.aspx/Get4DNumberCheckResultsJSON'
        HEADERS = {
            'Host': 'www.singaporepools.com.sg',
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }

        sg_tz = timezone(timedelta(hours=8))  # Singapore UTC+8

        def getDateFromDrawDate(x):
            if not x:
                return None
            try:
                ms = int(x.replace('/Date(', '').replace(')/', ''))
                utc_time = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
                sg_time = utc_time.astimezone(sg_tz)
                return sg_time.strftime('%Y-%m-%d')
            except:
                return None

        def GetResultsJson(num):
            data = json.dumps({
                "numbers": [str(num).zfill(4)],
                "checkCombinations": "true",
                "sortTypeInteger": "1"
            })
            r = requests.post(url=URL, data=data, headers=HEADERS)
            prizes = json.loads(r.json().get('d'))[0].get('Prizes')
            df = pd.DataFrame(prizes)
            if not df.empty:
                df["DrawDate"] = df["DrawDate"].apply(lambda x: getDateFromDrawDate(x))
                df["Digit"] = str(num).zfill(4)
                # Convert all object columns to string for Arrow compatibility
                for col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str)
            return df

        def getPermutation(n):
            return sorted(set(''.join(p) for p in itertools.permutations(n, 4)))

        def highlight_positive(s):
            return ['background-color: yellow' if v > 0 else '' for v in s > 0]

        def display_year_month_summary(df):
            if df.empty:
                st.write("No data available for Year-Month Summary.")
                return
            df = df.copy()
            df['DrawDate'] = pd.to_datetime(df['DrawDate'], errors='coerce')
            df = df.dropna(subset=['DrawDate'])
            if df.empty:
                st.write("No valid DrawDate data for Year-Month Summary.")
                return
            df['Year'] = df['DrawDate'].dt.year
            df['Month'] = df['DrawDate'].dt.month

            pivot = df.pivot_table(index='Year', columns='Month', values='Digit', aggfunc='count', fill_value=0)
            pivot.columns = [datetime(2000, m, 1).strftime('%b') for m in pivot.columns]
            pivot['Total'] = pivot.sum(axis=1)

            avg = pivot.mean(numeric_only=True).to_frame().T
            avg.index = ['Average']
            pivot = pivot.astype(int).sort_index(ascending=False)
            combined = pd.concat([avg, pivot])
            combined.index = combined.index.map(str)
            combined.columns = [str(c) for c in combined.columns]

            styled = (combined.style
                      .format({col: '{:.2f}' for col in combined.columns}, subset=pd.IndexSlice[['Average'], :])
                      .format({col: '{:.0f}' for col in combined.columns},
                              subset=pd.IndexSlice[combined.index.difference(['Average']), :])
                      .apply(highlight_positive)
                      .set_properties(**{'text-align': 'center'}))
            st.header("📊 Year-Month Summary Table")
            st.dataframe(styled, height=500)

        FreqAll = pd.DataFrame()

        for n in numberList:
            ResultsAll = pd.DataFrame()
            try:
                numbers = getPermutation(n) if genPermutation else [n]
                for num in numbers:
                    df = GetResultsJson(num)
                    if df is not None and not df.empty:
                        ResultsAll = pd.concat([ResultsAll, df], ignore_index=True)
                        # Show chart per permutation
                        if genPermutation:
                            with st.expander(label=num):
                                chart_df = df.set_index('DrawDate')['PrizeCode']
                                st.line_chart(chart_df, use_container_width=True)
                                st.dataframe(df['PrizeCode'].value_counts().sort_index())
            except Exception as e:
                st.error(f"Error fetching {n}: {e}")

            # Display per set
            if not ResultsAll.empty:
                with st.expander(label=f"Set: {n} / Total Freq: {ResultsAll.shape[0]}", expanded=True):
                    lineChartDF = ResultsAll.set_index('DrawDate')['PrizeCode'].sort_index(ascending=False)
                    st.line_chart(lineChartDF.head(15), use_container_width=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.dataframe(ResultsAll.sort_values('DrawDate', ascending=False))
                    with col2:
                        st_copy_to_clipboard(ResultsAll.sort_values('DrawDate')['Digit'].to_string(index=False, header=False))

                    st.dataframe(ResultsAll['PrizeCode'].value_counts().sort_index())

                    # Year-Month Summary
                    display_year_month_summary(ResultsAll)

                    # From Latest DrawNo
                    freq_df = ResultsAll['Digit'].value_counts().reset_index()
                    freq_df.columns = ['Digit', 'Frequency']
                    perm = "no" if genPermutation else "yes"
                    results = fetch_all_results(freq_df['Digit'], perm)
                    results_df = pd.DataFrame(results)
                    if not results_df.empty:
                        freq_df = freq_df.merge(results_df, left_on="Digit", right_on="digit").drop(columns=["digit"])
                        freq_df['url'] = freq_df['url'].apply(lambda x: f'<a href="{x}" target="_blank">link</a>')
                        st.write(freq_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                        FreqAll = pd.concat([FreqAll, freq_df], ignore_index=True)

        # Frequency summary download
        if not FreqAll.empty:
            FreqAll = FreqAll.groupby('Digit', as_index=False).agg({
                'Frequency': 'sum',
                'From Latest DrawNo': 'min'
            }).sort_values('Frequency', ascending=False)
            st.dataframe(FreqAll)
            st.markdown(download_link(FreqAll, '4D_Data.csv', '** ⬇️ Download as CSV file **'), unsafe_allow_html=True)

        st.markdown("<div style='text-align:right'><a href='#top'>------- ↟ Go to top ↟ -------</a></div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")

# -------------------------
# Parallel Fetcher
# -------------------------
def fetch_all_results(digits, perm, workers=20):
    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(get_from_latest_drawno, str(d), perm): d for d in digits}
        for future in as_completed(futures):
            results.append(future.result())
    return results

# -------------------------
# Utilities
# -------------------------
def filterList(numberList):
    return [num for num in (numberList or "").split() if num.isnumeric() and len(num) == 4]

def download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'

def scrapeLastRound():
    allResult = []
    start_url = "http://www.singaporepools.com.sg/DataFileArchive/Lottery/Output/fourd_result_draw_list_en.html"
    HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US, en;q=0.5'}
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

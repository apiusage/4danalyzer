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
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from collections import Counter
from itertools import product

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
        st.info("__Random Forest Prediction__")
        predict_4d_candidates("1st Prize", finalDF["1st Prize"].tolist())
        predict_4d_candidates("2nd Prize", finalDF["2nd Prize"].tolist())
        predict_4d_candidates("3rd Prize", finalDF["3rd Prize"].tolist())
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

# Random Forest Predictor
def predict_4d_candidates(prizeName, df_input):
    with st.expander(prizeName):
        # Convert string numbers into features
        def preprocess(numbers):
            data = []
            for num in numbers:
                if pd.isna(num):
                    continue  # skip NaNs
                num_str = str(int(num)).zfill(4)  # convert to int, then back to string with leading zeros if needed
                digits = [int(d) for d in num_str]

                digit_sum = sum(digits)
                odd_even = [d % 2 for d in digits]
                big_small = [1 if d >= 5 else 0 for d in digits]

                data.append({
                    'd1': digits[0], 'd2': digits[1], 'd3': digits[2], 'd4': digits[3],
                    'oe1': odd_even[0], 'oe2': odd_even[1], 'oe3': odd_even[2], 'oe4': odd_even[3],
                    'bs1': big_small[0], 'bs2': big_small[1], 'bs3': big_small[2], 'bs4': big_small[3],
                    'digit_sum': digit_sum
                })
            return pd.DataFrame(data)

        df = preprocess(df_input)

        # Prepare features and targets
        X_sum = df[['d1', 'd2', 'd3', 'd4', 'oe1', 'oe2', 'oe3', 'oe4', 'bs1', 'bs2', 'bs3', 'bs4']]
        y_sum = df['digit_sum']

        X_oe = df[['d1', 'd2', 'd3', 'd4']]
        y_oe = df[['oe1', 'oe2', 'oe3', 'oe4']]

        X_bs = df[['d1', 'd2', 'd3', 'd4']]
        y_bs = df[['bs1', 'bs2', 'bs3', 'bs4']]

        # Train digit sum regressor
        model_sum = RandomForestRegressor(n_estimators=100, random_state=42)
        model_sum.fit(X_sum, y_sum)

        # Train odd/even classifiers (one per digit)
        models_oe = []
        for i in range(4):
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_oe, y_oe.iloc[:, i])
            models_oe.append(clf)

        # Train big/small classifiers (one per digit)
        models_bs = []
        for i in range(4):
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_bs, y_bs.iloc[:, i])
            models_bs.append(clf)

        last_row = df.iloc[-1]
        input_sum = pd.DataFrame([{
            'd1': last_row.d1, 'd2': last_row.d2, 'd3': last_row.d3, 'd4': last_row.d4,
            'oe1': last_row.oe1, 'oe2': last_row.oe2, 'oe3': last_row.oe3, 'oe4': last_row.oe4,
            'bs1': last_row.bs1, 'bs2': last_row.bs2, 'bs3': last_row.bs3, 'bs4': last_row.bs4
        }])
        input_oe_bs = pd.DataFrame([{
            'd1': last_row.d1, 'd2': last_row.d2, 'd3': last_row.d3, 'd4': last_row.d4
        }])

        # Predict digit sum
        pred_sum_raw = model_sum.predict(input_sum)[0]

        # Find top 10 closest digit sums from history and their probabilities
        diffs = np.abs(df['digit_sum'] - pred_sum_raw)
        nearest_indices = diffs.nsmallest(10).index
        top10_sum = df.loc[nearest_indices, 'digit_sum']
        freq = Counter(top10_sum)
        total = sum(freq.values())
        top10_sum_prob = sorted([(s, freq[s] / total * 100) for s in freq], key=lambda x: x[1], reverse=True)

        st.header("🎲 Top 10 Digit Sum Predictions with Probabilities")
        sum_df = pd.DataFrame(top10_sum_prob, columns=["Digit Sum", "Probability (%)"])
        sum_df['Probability (%)'] = sum_df['Probability (%)'].map("{:.2f}%".format)
        st.table(sum_df)

        # Odd/Even probabilities per digit
        probs_oe = []
        for i, clf in enumerate(models_oe):
            proba_raw = clf.predict_proba(input_oe_bs)[0]
            classes = clf.classes_
            proba = [0.0, 0.0]  # index 0: even(0), index 1: odd(1)
            for j, cls in enumerate(classes):
                proba[cls] = proba_raw[j]
            probs_oe.append(proba)

        st.header("⚖️ Odd/Even Probabilities Per Digit")
        cols = st.columns(4)
        for i, proba in enumerate(probs_oe):
            with cols[i]:
                st.subheader(f"Digit {i+1}")
                st.markdown(f"- Even: **{proba[0]*100:.1f}%**")
                st.markdown(f"- Odd: **{proba[1]*100:.1f}%**")

        # Big/Small probabilities per digit
        probs_bs = []
        for i, clf in enumerate(models_bs):
            proba_raw = clf.predict_proba(input_oe_bs)[0]
            classes = clf.classes_
            proba = [0.0, 0.0]  # index 0: small(0), index 1: big(1)
            for j, cls in enumerate(classes):
                proba[cls] = proba_raw[j]
            probs_bs.append(proba)

        st.header("📊 Big/Small Probabilities Per Digit")
        cols = st.columns(4)
        for i, proba in enumerate(probs_bs):
            with cols[i]:
                st.subheader(f"Digit {i+1}")
                st.markdown(f"- Small: **{proba[0]*100:.1f}%**")
                st.markdown(f"- Big: **{proba[1]*100:.1f}%**")

        # Decide possible options per digit based on probability difference threshold (0.3)
        oe_options = [
            [0, 1] if abs(probs[0] - probs[1]) < 0.3 else [np.argmax(probs)]
            for probs in probs_oe
        ]
        bs_options = [
            [0, 1] if abs(probs[0] - probs[1]) < 0.3 else [np.argmax(probs)]
            for probs in probs_bs
        ]

        oe_patterns = list(product(*oe_options))
        bs_patterns = list(product(*bs_options))

        top10_sums = [s for s, _ in top10_sum_prob]

        st.markdown("---")
        st.write("🔍 Generating candidate 4D numbers based on predicted patterns...")

        # Convert historical input numbers into set for quick exclusion
        input_numbers_set = set(str(int(num)).zfill(4) for num in df_input if pd.notna(num))

        def matches_patterns(num_str, digit_sum_target, oe_pattern, bs_pattern):
            digits = [int(d) for d in num_str]
            if sum(digits) != digit_sum_target:
                return False
            for i in range(4):
                oe = digits[i] % 2
                bs = 1 if digits[i] >= 5 else 0
                if oe != oe_pattern[i] or bs != bs_pattern[i]:
                    return False
            return True

        candidates = []
        for ds in top10_sums:
            for oe_p in oe_patterns:
                for bs_p in bs_patterns:
                    for n in range(10000):
                        s = f"{n:04d}"
                        if s in input_numbers_set:
                            continue  # exclude historical numbers
                        if matches_patterns(s, ds, oe_p, bs_p):
                            candidates.append(s)

        st.success(f"Found **{len(candidates)}** candidate numbers matching predicted patterns.\n")

        if candidates:
            st.subheader("Sample Candidate Numbers (up to 30 shown)")
            st.write(' '.join(candidates))
        else:
            st.warning("No new candidates found matching the predicted patterns.")

        return candidates

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

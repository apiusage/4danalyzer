import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re, time
import xgboost as xgb
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import concurrent.futures

# Constants
DOUBLE_DIGITS = [f"{i}{i}" for i in range(10)]
TIME_TABS = ["📊 All", "📅 6 Months", "📆 14 Days", "📆 1 Month", "📈 1 Year"]
TIME_DAYS = {"📅 6 Months": 180, "📆 14 Days": 14, "📆 1 Month": 30, "📈 1 Year": 365}
TREND_TABS = ["📅 2 Months", "📅 6 Months", "📅 14 Days", "📆 1 Month", "📈 1 Year"]
TREND_DAYS = {"📅 2 Months": 60, "📅 6 Months": 180, "📅 14 Days": 14, "📆 1 Month": 30, "📈 1 Year": 365}

@st.cache_data(ttl=3600)
def load_data(url="https://raw.githubusercontent.com/apiusage/sg-4d-json/refs/heads/main/4d_results.csv"):
    df = pd.read_csv(url).dropna(how='all')
    df['DrawDate'] = pd.to_datetime(df['DrawDate'], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['DrawDate'])
    for prize in ['1st', '2nd', '3rd']:
        df[prize] = df[prize].astype(str).str.zfill(4)
    return df

def fetch_4d_json():
    try:
        r = requests.get('https://raw.githubusercontent.com/apiusage/sg-4d-json/main/4d.json', timeout=5)
        r.raise_for_status()
        return r.json()
    except:
        return None

def get_2d():
    nums = fetch_4d_json()
    if not nums:
        return "", ""
    n = str(nums[0]).zfill(4)
    a, b = (int(n[0]) + int(n[1])) % 10, (int(n[2]) + int(n[3])) % 10
    first = sum(int(d) for d in str(int(n[0]) + int(n[1]))) % 10
    return f"{a}{b}", f"{first}{(int(n[2]) + int(n[3])) % 10}"

def double_digit_count(numbers, dates):
    rows = [(dd, len(hits), sorted(hits, reverse=True)[:20])
            for dd in DOUBLE_DIGITS if (hits := [d for n, d in zip(numbers, dates) if dd in n])]
    return pd.DataFrame(rows, columns=['DoubleDigit', 'Frequency', 'LastDates']).sort_values('Frequency',
                                                                                             ascending=False,
                                                                                             ignore_index=True)

def double_digits_stats(numbers, dates, prize_name):
    st.markdown("### 🔁 Double Digits (e.g., 00, 11 …)")
    dd_df = double_digit_count(numbers, dates)
    st.dataframe(dd_df[['DoubleDigit', 'Frequency']], use_container_width=True)

    sel = st.selectbox(f"Select Double Digit in {prize_name}", dd_df['DoubleDigit'], key=f"dd_{prize_name}")
    draw_dates = pd.to_datetime(dd_df.set_index('DoubleDigit').loc[sel, 'LastDates'])

    tl_df = pd.DataFrame({
        'DrawDate': draw_dates.strftime('%Y-%m-%d (%a)'),
        'GapInDays': pd.Series(draw_dates.diff()).abs().dt.days.fillna(0).astype(int)
    })

    avg_row = pd.DataFrame([{'DrawDate': 'Average', 'GapInDays': int(round(tl_df['GapInDays'][1:].mean()))}])
    tl_df_display = pd.concat([avg_row, tl_df], ignore_index=True)

    st.write(tl_df_display.style.apply(
        lambda r: ['background-color: #ffff99' if r.name == 0 else '' for _ in r], axis=1
    ))

def get_digit_pattern(num, mode):
    num = str(num).zfill(4)
    return ''.join('H' if int(d) >= 5 else 'L' for d in num) if mode == 'highlow' else ''.join(
        'E' if int(d) % 2 == 0 else 'O' for d in num)

def digit_pattern_count(numbers, mode):
    return pd.DataFrame(Counter([get_digit_pattern(n, mode) for n in numbers]).items(),
                        columns=['Pattern', 'Frequency']).sort_values('Frequency', ascending=False)

def digit_pattern_count_tabs(df, prize_name, mode):
    tabs = st.tabs(TIME_TABS)
    for tab, title in zip(tabs, TIME_TABS):
        with tab:
            filt = df if title == "📊 All" else df[
                df['DrawDate'] >= pd.Timestamp.today() - pd.Timedelta(days=TIME_DAYS[title])]
            if filt.empty:
                st.warning("No data")
                continue
            patt_df = digit_pattern_count(filt[prize_name].astype(str).str.zfill(4), mode)
            st.dataframe(patt_df, use_container_width=True)
            st.bar_chart(patt_df.set_index('Pattern')['Frequency'])

def digit_position_trends_tabs(df, prize_name):
    st.markdown("### 📈 Digit Position Trends")
    tabs = st.tabs(TREND_TABS)
    for tab, title in zip(tabs, TREND_TABS):
        with tab:
            filt = df[df['DrawDate'] >= pd.Timestamp.today() - pd.Timedelta(days=TREND_DAYS[title])].sort_values(
                'DrawDate')
            if filt.empty:
                st.warning("No data")
                continue
            nums = filt[prize_name].astype(str).str.zfill(4).tolist()
            for i in range(4):
                st.info(f'Digit {i + 1}')
                st.line_chart(pd.DataFrame({f'Digit {i + 1}': [int(n[i]) for n in nums]}))

def plot_digit_sum_trend(df, prize_name):
    st.markdown(f"### ➕ Digit Sum Trend ({prize_name})")
    tabs = st.tabs(TREND_TABS)
    for tab, title in zip(tabs, TREND_TABS):
        with tab:
            filt = df[df['DrawDate'] >= pd.Timestamp.today() - pd.Timedelta(days=TREND_DAYS[title])].sort_values(
                'DrawDate')
            if filt.empty:
                st.warning("No data")
                continue
            chart_df = pd.DataFrame({
                'DrawDate': filt['DrawDate'],
                'DigitSum': filt[prize_name].astype(str).str.zfill(4).apply(lambda x: sum(map(int, x)))
            })
            st.plotly_chart(px.line(chart_df, x='DrawDate', y='DigitSum', title=f"{title} • Digit Sum",
                                    labels={'DrawDate': 'Draw Date', 'DigitSum': 'Sum'}), use_container_width=True)
            st.dataframe(chart_df['DigitSum'].agg(['mean', 'max', 'min', 'std']).round(2)
                         .rename({'mean': 'Average', 'std': 'Std Dev'}).to_frame('Value'))

def prize_digit_breakdown(df, prize_name):
    st.markdown(f"### 🔢 Digit Frequency per {prize_name} Prize (Latest 100)")

    recent = df[['DrawDate', prize_name]].dropna().sort_values('DrawDate', ascending=False).head(100).reset_index(
        drop=True)
    recent[prize_name] = recent[prize_name].astype(str).str.zfill(4)

    digit_cols = [str(i) for i in range(10)]
    freq = [[num.count(str(d)) for d in range(10)] for num in recent[prize_name]]
    summary_df = pd.DataFrame(freq, columns=digit_cols)
    summary_df.insert(0, 'Number', recent[prize_name])

    avg = summary_df[digit_cols].mean().round(3)
    avg_row = pd.DataFrame([['Average', *avg.tolist()]], columns=['Number'] + digit_cols)
    summary_df = pd.concat([avg_row, summary_df], ignore_index=True)

    styled_df = (summary_df.style
                 .apply(lambda r: ['background-color: lightblue; font-weight: bold'] * len(r) if r[
                                                                                                     'Number'] == 'Average' else [''] * len(
        r), axis=1)
                 .map(lambda v: 'background-color: yellow' if (isinstance(v, (int, float)) and float(v) > 0) else '',
                      subset=pd.IndexSlice[1:, digit_cols])
                 .format({col: "{:.3f}" for col in digit_cols}, subset=pd.IndexSlice[[0], digit_cols])
                 .format({col: "{:.0f}" for col in digit_cols}, subset=pd.IndexSlice[1:, digit_cols])
                 .set_properties(**{'text-align': 'center'})
                 .set_properties(subset=pd.IndexSlice[[0], :], **{'font-weight': 'bold'}))

    st.dataframe(styled_df, use_container_width=True)

def analyze_prize(df, prize_name):
    numbers = df[prize_name].astype(str).str.zfill(4)

    st.markdown(f"### 🏆 Most Frequent {prize_name} Numbers")
    st.dataframe(numbers.value_counts().reset_index(name='Frequency').rename(columns={'index': 'Number'}).head(200),
                 use_container_width=True)

    st.markdown("### 🔢 Digit-by-Position Frequency")
    tabs = st.tabs(TIME_TABS)
    for tab, title in zip(tabs, TIME_TABS):
        with tab:
            filt = df if title == "📊 All" else df[
                df['DrawDate'] >= df['DrawDate'].max() - pd.Timedelta(days=TIME_DAYS[title])]
            if filt.empty:
                st.warning("No data")
                continue
            nums_f = filt[prize_name].astype(str).str.zfill(4)
            for i in range(4):
                freq = nums_f.str[i].value_counts().sort_index()
                st.plotly_chart(px.bar(x=freq.index, y=freq.values, labels={'x': f'Digit {i + 1}', 'y': 'Frequency'},
                                       title=f"{title} • Digit {i + 1}"), use_container_width=True,
                                key=f"{prize_name}_{title}_pos{i}")

    double_digits_stats(numbers, df['DrawDate'], prize_name)
    digit_position_trends_tabs(df, prize_name)
    plot_digit_sum_trend(df, prize_name)

    st.markdown("### 🔡 High–Low & Even–Odd Patterns")
    digit_pattern_count_tabs(df, prize_name, 'highlow')
    st.markdown("#### Even-Odd (E = Even, O = Odd)")
    digit_pattern_count_tabs(df, prize_name, 'evenodd')

    st.success(f"✅ Total Numbers Analyzed: {len(numbers)}")

def digitSumTable():
    df = load_data()
    st.markdown("### 📊 Last 200 Draws with All Prizes & Digit Sums")

    # Convert DrawDate to date only
    df['DrawDate'] = pd.to_datetime(df['DrawDate']).dt.date

    wide_df = df[['DrawDate', '1st', '2nd', '3rd']].copy()
    for col in ['1st', '2nd', '3rd']:
        wide_df[f'sum_{col}'] = wide_df[col].apply(lambda x: sum(map(int, str(x))) if str(x).isdigit() else None)

    st.dataframe(wide_df[['DrawDate', '1st', '2nd', '3rd', 'sum_1st', 'sum_2nd', 'sum_3rd']]
                 .tail(200).iloc[::-1]
                 .rename(columns={'DrawDate': 'Date', '1st': '1st Prize', '2nd': '2nd Prize', '3rd': '3rd Prize',
                                  'sum_1st': 'DS (1st)', 'sum_2nd': 'DS (2nd)', 'sum_3rd': 'DS (3rd)'})
                 .reset_index(drop=True))

def transformationMethod():
    opts = Options();
    opts.add_argument('--headless')
    d = webdriver.Chrome(options=opts)
    d.get("https://www.singaporepools.com.sg/en/product/pages/4d_results.aspx")
    time.sleep(3)
    s = BeautifulSoup(d.page_source, 'html.parser');
    d.quit()

    f = s.select_one('ul.ulDraws > li')
    A = str(9999 - int(f.find('td', class_='tdFirstPrize').text.strip())).zfill(4).translate(
        str.maketrans("0123456789", "5678901234"))
    B = re.search(r'\d+', f.find('th', class_='drawNumber').text).group()[-3:].zfill(4)
    C = re.search(r'\b0?(\d{1,2})\b',
                  next(filter(lambda x: "am" in x.text or "pm" in x.text, s.select('div.col-md-9 > div'))).text).group(
        1).zfill(2)
    Ai, Bi, Ci = map(int, [A, B, C])

    R = [str((Ai + Bi + Ci) % 10000).zfill(4), str((Ai + Bi - Ci) % 10000).zfill(4),
         str((Ai - Bi - Ci) % 10000).zfill(4), str((Ai - Bi + Ci) % 10000).zfill(4)]
    p = [int(f.find('td', class_=f'td{pos}Prize').text.strip()) for pos in ['First', 'Second', 'Third']]
    hist = [str((x + 1234) % 10000).zfill(4) for x in p]
    zero8782 = [str(round(x * 0.8782)).zfill(4) for x in p]

    with st.expander("🎲 Transformation Results", True):
        [st.markdown(f"**{i}.** `{r}`") for i, r in enumerate(R, 1)]
    with st.expander("🎲 Historical Method Results", True):
        [st.markdown(f"**{i}.** `{r}`") for i, r in enumerate(hist, 1)]
    with st.expander("🎲 0.8782 Calculation (1st, 2nd, 3rd Prize)", True):
        [st.markdown(f"**{pos} Prize:** `{val}`") for pos, val in zip(['1st', '2nd', '3rd'], zero8782)]

def run_setAnalysis():
    df = load_data()

    for prize in ['1st', '2nd', '3rd']:
        with st.expander(f"🎯 {prize} Prize Analysis"):
            prize_digit_breakdown(df, prize)
            analyze_prize(df, prize)

    digitSumTable()

    out1, out2 = get_2d()
    st.write("**2D:**", out1, out2)
    transformationMethod()

if __name__ == "__main__":
    run_setAnalysis()
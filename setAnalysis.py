import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import requests

# ML imports
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

DOUBLE_DIGITS = [f"{i}{i}" for i in range(10)]  # 00, 11, ..., 99

def run_setAnalysis():
    st.title("🎲 Singapore Pools 4D Analyzer")

    output1, output2 = get_2d()
    st.write("**2D:** " + output1 + " " + output2)

    # Load CSV and drop rows that are completely empty
    df = pd.read_csv("https://raw.githubusercontent.com/apiusage/sg-4d-json/refs/heads/main/4d_results.csv")
    df = df.dropna(how='all')  # Drop rows where all fields are NaN

    # Parse dates
    df['DrawDate'] = pd.to_datetime(df['DrawDate'], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['DrawDate'])  # Drop rows without a valid date

    # Zero-pad all prize columns to 4 digits
    for prize in ['1st', '2nd', '3rd']:
        df[prize] = df[prize].astype(str).str.zfill(4)

    # Analyze for 1st, 2nd, 3rd
    for prize in ['1st', '2nd', '3rd']:
        with st.expander(f"🎯 {prize} Prize Analysis"):
            analyze_prize(df, prize)

def fetch_4d_json():
    url = 'https://raw.githubusercontent.com/apiusage/sg-4d-json/main/4d.json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching 4D JSON: {e}")
        return None

# https://www.youtube.com/watch?v=FD6ntv0aU6M
def get_2d():
    numbers = fetch_4d_json()
    if not numbers:
        return "", ""  # Return two empty strings on error
    n = str(numbers[0]).zfill(4)
    n = str(9999)
    # 1st 2D
    a = (int(n[0]) + int(n[1])) % 10
    b = (int(n[2]) + int(n[3])) % 10
    output1 = f"{a}{b}"

    # 2nd 2D
    first = (sum(int(d) for d in str(int(n[0]) + int(n[1])))) % 10
    second = (int(n[2]) + int(n[3])) % 10
    output2 = f"{first}{second}"

    return output1, output2

def analyze_prize(df, prize_name):
    numbers = df[prize_name].astype(str).str.zfill(4)
    dates = df['DrawDate']

    st.markdown(f"### 🏆 Most Frequent {prize_name} Numbers")
    freq_df = numbers.value_counts().reset_index()
    freq_df.columns = ['Number', 'Frequency']
    st.dataframe(freq_df)

    st.markdown("### 🔢 Digit-by-Position Frequency")
    for i in range(4):
        digit_freq = numbers.str[i].value_counts().sort_index()
        fig = px.bar(x=digit_freq.index, y=digit_freq.values,
                     labels={'x': f"Digit {i+1}", 'y': 'Frequency'},
                     title=f"{prize_name} – Digit Position {i+1}")
        st.plotly_chart(fig, use_container_width=True, key=f"{prize_name}_pos{i}")

    st.markdown("### 🔁 Double Digits (e.g., 00, 11, ...)")
    double_df = double_digit_count(numbers, dates)
    st.dataframe(double_df[['DoubleDigit', 'Frequency']])

    selected = st.selectbox(f"Select Double Digit in {prize_name}", double_df['DoubleDigit'], key=prize_name)
    recent_dates = double_df.set_index('DoubleDigit').loc[selected, 'LastDates']

    timeline_df = pd.DataFrame({
        'DrawDate': pd.to_datetime(recent_dates),
        'Occurrence': list(range(len(recent_dates), 0, -1))
    }).sort_values('DrawDate')

    fig = px.bar(
        timeline_df,
        x='DrawDate',
        y='Occurrence',
        title=f"Last 20 Times {selected} Appeared in {prize_name}"
    )
    st.plotly_chart(fig, use_container_width=True, key=f"{prize_name}_double")

    st.markdown("### 📈 Digit Position Trends (Last 20 Draws)")
    recent_20 = df.sort_values('DrawDate').tail(20)[prize_name].astype(str).str.zfill(4).tolist()[::-1]
    digitAnalysis(recent_20)

    plot_digit_sum_trend(df, prize_name)

    st.markdown("### 🔡 High–Low & Even–Odd Patterns")
    hl_df = digit_pattern_count(numbers, 'highlow')
    eo_df = digit_pattern_count(numbers, 'evenodd')

    st.markdown("**High–Low (L=0–4, H=5–9)**")
    st.dataframe(hl_df)
    st.plotly_chart(px.bar(hl_df, x='Pattern', y='Frequency', title=f"{prize_name} H/L Patterns"),
                    use_container_width=True, key=f"{prize_name}_hl")

    st.markdown("**Even–Odd (E=Even, O=Odd)**")
    st.dataframe(eo_df)
    st.plotly_chart(px.bar(eo_df, x='Pattern', y='Frequency', title=f"{prize_name} E/O Patterns"),
                    use_container_width=True, key=f"{prize_name}_eo")

    st.success(f"✅ Total Numbers Analyzed: {len(numbers)}")

    # Add prediction
    # predict_next_number(df, prize_name)

def double_digit_count(numbers, dates):
    results = []
    for dd in DOUBLE_DIGITS:
        matched = []
        for num, date in zip(numbers, dates):
            if dd in num:
                matched.append(date)
        if matched:
            results.append((dd, len(matched), matched[-20:]))
    df = pd.DataFrame(results, columns=['DoubleDigit', 'Frequency', 'LastDates'])
    return df.sort_values(by='Frequency', ascending=False)

def get_digit_pattern(num, mode='highlow'):
    num = str(num).zfill(4)
    if mode == 'highlow':
        return ''.join(['H' if int(d) >= 5 else 'L' for d in num])
    elif mode == 'evenodd':
        return ''.join(['E' if int(d) % 2 == 0 else 'O' for d in num])

def digit_pattern_count(numbers, mode='highlow'):
    patterns = [get_digit_pattern(n, mode) for n in numbers]
    df = pd.DataFrame(Counter(patterns).items(), columns=['Pattern', 'Frequency'])
    df = df.sort_values(by='Frequency', ascending=False)
    return df

def digitAnalysis(numberList):
    digit1Data, digit2Data, digit3Data, digit4Data = [], [], [], []

    if numberList is not None:
        for num in numberList:
            digit1Data.insert(0, int(num[0]))
            digit2Data.insert(0, int(num[1]))
            digit3Data.insert(0, int(num[2]))
            digit4Data.insert(0, int(num[3]))

    st.info("Digit 1")
    st.line_chart(pd.DataFrame({'Digit 1': digit1Data}))

    st.info("Digit 2")
    st.line_chart(pd.DataFrame({'Digit 2': digit2Data}))

    st.info("Digit 3")
    st.line_chart(pd.DataFrame({'Digit 3': digit3Data}))

    st.info("Digit 4")
    st.line_chart(pd.DataFrame({'Digit 4': digit4Data}))

def plot_digit_sum_trend(df, prize_name):
    st.markdown(f"### ➕ Digit Sum Trend – Last 30 Draws ({prize_name})")

    # Sort and get last 30 draws
    df_sorted = df.sort_values("DrawDate").tail(30)
    numbers = df_sorted[prize_name].astype(str).str.zfill(4)
    digit_sums = numbers.apply(lambda x: sum(int(d) for d in x))

    chart_data = pd.DataFrame({
        'DrawDate': df_sorted['DrawDate'],
        'DigitSum': digit_sums
    })

    # Plot line chart
    fig = px.line(chart_data, x='DrawDate', y='DigitSum',
                  labels={'DrawDate': 'Draw Date', 'DigitSum': 'Digit Sum'})
    st.plotly_chart(fig, use_container_width=True, key=f"{prize_name}_digitsum")

    # Stats
    avg_sum = digit_sums.mean()
    max_sum = digit_sums.max()
    min_sum = digit_sums.min()
    std_sum = digit_sums.std()

    st.markdown("#### 📊 Digit Sum Statistics (Last 20 Draws)")
    stats_df = pd.DataFrame({
        'Statistic': ['Average', 'Maximum', 'Minimum', 'Standard Deviation'],
        'Value': [round(avg_sum, 2), max_sum, min_sum, round(std_sum, 2)]
    })

    st.dataframe(stats_df, use_container_width=True)

def predict_next_number(df, prize_name):
    st.markdown("### 🤖 ML Predictions for Next Likely Number")

    df_sorted = df.sort_values('DrawDate')
    numbers = df_sorted[prize_name].astype(str).str.zfill(4)

    features = []
    targets = []

    for i in range(len(numbers) - 1):
        current = numbers.iloc[i]
        next_num = numbers.iloc[i + 1]
        feat = [
            int(current[0]), int(current[1]), int(current[2]), int(current[3]),
            sum(1 for d in current if int(d) >= 5),
            sum(1 for d in current if int(d) % 2 == 0)
        ]
        features.append(feat)
        targets.append(next_num)

    if len(features) < 10:
        st.warning("Not enough data to train ML model.")
        return

    le = LabelEncoder()
    y_encoded = le.fit_transform(targets)
    X_train, X_test, y_train, y_test = train_test_split(features, y_encoded, test_size=0.2, random_state=42)

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train, y_train)

    last = numbers.iloc[-1]
    last_feat = [[
        int(last[0]), int(last[1]), int(last[2]), int(last[3]),
        sum(1 for d in last if int(d) >= 5),
        sum(1 for d in last if int(d) % 2 == 0)
    ]]

    rf_pred = le.inverse_transform(rf.predict(last_feat))[0]
    knn_pred = le.inverse_transform(knn.predict(last_feat))[0]

    st.info(f"📌 Last {prize_name} number: **{last}**")
    st.success(f"🔮 Random Forest Prediction: **{rf_pred}**")
    st.success(f"🔮 KNN Prediction: **{knn_pred}**")
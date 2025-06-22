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

    # Analyze for 1st, 2nd, 3rd prizes
    for prize in ['1st', '2nd', '3rd']:
        with st.expander(f"🎯 {prize} Prize Analysis"):
            prize_digit_breakdown(df, prize)
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

def get_2d():
    numbers = fetch_4d_json()
    if not numbers:
        return "", ""  # Return two empty strings on error
    n = str(numbers[0]).zfill(4)
    # You override n to "9999" in your code — keep it or remove?
    n = "9999"
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
    st.dataframe(freq_df.head(200), use_container_width=True)

    st.markdown("### 🔢 Digit-by-Position Frequency")
    for i in range(4):
        digit_freq = numbers.str[i].value_counts().sort_index()
        fig = px.bar(
            x=digit_freq.index, y=digit_freq.values,
            labels={'x': f"Digit {i+1}", 'y': 'Frequency'},
            title=f"{prize_name} – Digit Position {i+1}"
        )
        st.plotly_chart(fig, use_container_width=True, key=f"{prize_name}_pos{i}")

    st.markdown("### 🔁 Double Digits (e.g., 00, 11, ...)")
    double_df = double_digit_count(numbers, dates)
    st.dataframe(double_df[['DoubleDigit', 'Frequency']], use_container_width=True)

    selected = st.selectbox(f"Select Double Digit in {prize_name}", double_df['DoubleDigit'], key=f"double_{prize_name}")
    recent_dates = double_df.set_index('DoubleDigit').loc[selected, 'LastDates']

    timeline_df = pd.DataFrame({
        'DrawDate': pd.to_datetime(recent_dates)
    }).sort_values('DrawDate').reset_index(drop=True)

    timeline_df['GapInDays'] = timeline_df['DrawDate'].diff().dt.days.fillna(0)

    fig = px.bar(
        timeline_df,
        x='DrawDate',
        y='GapInDays',
        title=f"Gaps Between Last 20 {selected} in {prize_name} (in Days)",
        labels={'DrawDate': 'Draw Date', 'GapInDays': 'Gap (Days)'}
    )
    st.plotly_chart(fig, use_container_width=True)

    digit_position_trends_tabs(df, prize_name)

    plot_digit_sum_trend(df, prize_name)

    st.markdown("### 🔡 High–Low & Even–Odd Patterns")

    digit_pattern_count_tabs(df, prize_name, 'highlow')

    st.markdown("#### Even-Odd (E=Even, O=Odd)")
    digit_pattern_count_tabs(df, prize_name, 'evenodd')

    st.success(f"✅ Total Numbers Analyzed: {len(numbers)}")

def double_digit_count(numbers, dates):
    results = []
    for dd in DOUBLE_DIGITS:
        matched = [date for num, date in zip(numbers, dates) if dd in num]
        if matched:
            # Sort dates descending and pick last 20 latest dates
            matched_sorted = sorted(matched, reverse=True)[:20]
            results.append((dd, len(matched), matched_sorted))
    df = pd.DataFrame(results, columns=['DoubleDigit', 'Frequency', 'LastDates'])
    return df.sort_values(by='Frequency', ascending=False).reset_index(drop=True)

def get_digit_pattern(num, mode='highlow'):
    num = str(num).zfill(4)
    if mode == 'highlow':
        return ''.join(['H' if int(d) >= 5 else 'L' for d in num])
    elif mode == 'evenodd':
        return ''.join(['E' if int(d) % 2 == 0 else 'O' for d in num])
    return ''

def digit_pattern_count(numbers, mode='highlow'):
    patterns = [get_digit_pattern(n, mode) for n in numbers]
    df = pd.DataFrame(Counter(patterns).items(), columns=['Pattern', 'Frequency'])
    df = df.sort_values(by='Frequency', ascending=False)
    return df

def digit_pattern_count_tabs(df, prize_name, mode='highlow'):
    tab_titles = ["📊 All", "📅 6 Months", "📆 14 Days", "📆 1 Month", "📈 1 Year"]
    days_map = {
        "📅 6 Months": 180,
        "📆 14 Days": 14,
        "📆 1 Month": 30,
        "📈 1 Year": 365
    }

    tabs = st.tabs(tab_titles)

    for tab_title, tab in zip(tab_titles, tabs):
        with tab:
            if tab_title == "📊 All":
                filtered = df
            else:
                cutoff = pd.Timestamp.today() - pd.Timedelta(days=days_map[tab_title])
                filtered = df[df['DrawDate'] >= cutoff]

            if filtered.empty:
                st.warning("No data available for this time range.")
                continue

            numbers = filtered[prize_name].astype(str).str.zfill(4).tolist()
            pattern_df = digit_pattern_count(numbers, mode)
            st.dataframe(pattern_df, use_container_width=True)
            st.bar_chart(pattern_df.set_index('Pattern')['Frequency'])

def digit_position_trends_tabs(df, prize_name):
    st.markdown("### 📈 Digit Position Trends")

    tab_titles = ["📅 2 Months", "📅 6 Months", "📅 14 Days", "📆 1 Month", "📈 1 Year"]
    days_map = {
        "📅 2 Months": 60,
        "📅 6 Months": 180,
        "📅 14 Days": 14,
        "📆 1 Month": 30,
        "📈 1 Year": 365
    }

    tabs = st.tabs(tab_titles)

    for tab_title, tab in zip(tab_titles, tabs):
        with tab:
            days = days_map[tab_title]
            cutoff = pd.Timestamp.today() - pd.Timedelta(days=days)
            filtered = df[df['DrawDate'] >= cutoff].sort_values('DrawDate')

            if filtered.empty:
                st.warning(f"No data available for the past {days} days.")
                continue

            numbers_list = filtered[prize_name].astype(str).str.zfill(4).tolist()

            digit1Data, digit2Data, digit3Data, digit4Data = [], [], [], []

            for num in numbers_list:
                # Append in natural order so time flows left-to-right (old to new)
                digit1Data.append(int(num[0]))
                digit2Data.append(int(num[1]))
                digit3Data.append(int(num[2]))
                digit4Data.append(int(num[3]))

            st.info("Digit 1")
            st.line_chart(pd.DataFrame({'Digit 1': digit1Data}))

            st.info("Digit 2")
            st.line_chart(pd.DataFrame({'Digit 2': digit2Data}))

            st.info("Digit 3")
            st.line_chart(pd.DataFrame({'Digit 3': digit3Data}))

            st.info("Digit 4")
            st.line_chart(pd.DataFrame({'Digit 4': digit4Data}))

def plot_digit_sum_trend(df, prize_name):
    st.markdown(f"### ➕ Digit Sum Trend ({prize_name})")

    tab60, tab180, tab14, tab30, tab365 = st.tabs(["📅 2 Months", "📅 6 Months", "📅 14 Days", "📆 1 Month", "📈 1 Year"])
    tab_map = {
        tab60: 60,
        tab180: 180,
        tab14: 14,
        tab30: 30,
        tab365: 365
    }

    for tab, days in tab_map.items():
        with tab:
            st.markdown(f"#### Showing digit sums for the past {days} days")

            cutoff_date = pd.Timestamp.today() - pd.Timedelta(days=days)
            df_filtered = df[df['DrawDate'] >= cutoff_date].sort_values("DrawDate")

            if df_filtered.empty:
                st.warning("No data available for this time range.")
                continue

            numbers = df_filtered[prize_name].astype(str).str.zfill(4)
            digit_sums = numbers.apply(lambda x: sum(int(d) for d in x))

            chart_data = pd.DataFrame({
                'DrawDate': df_filtered['DrawDate'],
                'DigitSum': digit_sums
            })

            fig = px.line(
                chart_data, x='DrawDate', y='DigitSum',
                labels={'DrawDate': 'Draw Date', 'DigitSum': 'Digit Sum'},
                title=f"{prize_name} Digit Sum Trend – Last {days} Days"
            )
            st.plotly_chart(fig, use_container_width=True, key=f"{prize_name}_digitsum_{days}")

            avg_sum = digit_sums.mean()
            max_sum = digit_sums.max()
            min_sum = digit_sums.min()
            std_sum = digit_sums.std()

            st.markdown("#### 📊 Digit Sum Statistics")
            stats_df = pd.DataFrame({
                'Statistic': ['Average', 'Maximum', 'Minimum', 'Standard Deviation'],
                'Value': [round(avg_sum, 2), max_sum, min_sum, round(std_sum, 2)]
            })

            st.dataframe(stats_df, use_container_width=True)

def prize_digit_breakdown(df, prize_name):
    st.markdown(f"### 🔢 Digit Frequency per {prize_name} Prize Number (Latest 100)")

    df = df[['DrawDate', prize_name]].dropna()
    df['DrawDate'] = pd.to_datetime(df['DrawDate'])
    df[prize_name] = df[prize_name].astype(str).str.zfill(4)
    df = df.sort_values('DrawDate', ascending=False).head(100)

    digit_cols = [str(d) for d in range(10)]
    freq_data = [[num.count(str(d)) for d in range(10)] for num in df[prize_name]]
    numbers = df[prize_name].tolist()

    summary_df = pd.DataFrame(freq_data, columns=digit_cols)
    summary_df.insert(0, 'Number', numbers)
    summary_df = summary_df.drop_duplicates(subset='Number')

    avg_values = summary_df[digit_cols].mean().round(3)
    avg_row = pd.DataFrame([['Average'] + avg_values.tolist()], columns=['Number'] + digit_cols)

    summary_df = pd.concat([avg_row, summary_df], ignore_index=True)
    summary_df.loc[1:, digit_cols] = summary_df.loc[1:, digit_cols].astype(int)

    def highlight_nonzero(val):
        try:
            return 'background-color: yellow' if float(val) > 0 else ''
        except:
            return ''

    def highlight_average(row):
        if row['Number'] == 'Average':
            return ['background-color: lightblue; font-weight: bold'] * len(row)
        return [''] * len(row)

    styled_df = (
        summary_df.style
        .apply(highlight_average, axis=1)
        .map(highlight_nonzero, subset=pd.IndexSlice[1:, digit_cols])
        .format(precision=3, subset=pd.IndexSlice[0, digit_cols])
        .format(precision=0, subset=pd.IndexSlice[1:, digit_cols])
        .set_properties(**{'text-align': 'center'})
    )

    st.dataframe(styled_df, use_container_width=True)

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

if __name__ == "__main__":
    run_setAnalysis()

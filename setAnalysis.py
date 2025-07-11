import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import requests
# ML imports
import xgboost as xgb
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
# ────────────────────────────────────────────────────────────────
# 🔧 GLOBAL CONSTANTS
# ────────────────────────────────────────────────────────────────
DOUBLE_DIGITS = [f"{i}{i}" for i in range(10)]          # 00, 11, …

# Generic time-filter tabs (includes “All”)
TIME_TABS = ["📊 All", "📅 6 Months", "📆 14 Days", "📆 1 Month", "📈 1 Year"]
TIME_DAYS = {"📅 6 Months": 180, "📆 14 Days": 14, "📆 1 Month": 30, "📈 1 Year": 365}

# Trend tabs (no “All”, but adds “2 Months”)
TREND_TABS = ["📅 2 Months", "📅 6 Months", "📅 14 Days", "📆 1 Month", "📈 1 Year"]
TREND_DAYS = {"📅 2 Months": 60, "📅 6 Months": 180,
              "📅 14 Days": 14, "📆 1 Month": 30, "📈 1 Year": 365}
# ────────────────────────────────────────────────────────────────
# ╭───────────────────────────────╮
# |      MAIN STREAMLIT APP       |
# ╰───────────────────────────────╯
def run_setAnalysis():
    st.title("🎲 Singapore Pools 4D Analyzer")

    # quick 2-D numbers
    out1, out2 = get_2d()
    st.write("**2D:**", out1, out2)

    # predict_4d_digit_sums_xgboost()

    # load & clean CSV
    url = "https://raw.githubusercontent.com/apiusage/sg-4d-json/refs/heads/main/4d_results.csv"
    df = pd.read_csv(url).dropna(how='all')
    df['DrawDate'] = pd.to_datetime(df['DrawDate'], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['DrawDate'])

    # zero-pad prize numbers
    for prize in ['1st', '2nd', '3rd']:
        df[prize] = df[prize].astype(str).str.zfill(4)

    # analyse each prize
    for prize in ['1st', '2nd', '3rd']:
        with st.expander(f"🎯 {prize} Prize Analysis"):
            prize_digit_breakdown(df, prize)
            analyze_prize(df, prize)

# ╭───────────────────────────────╮
# |      DATA FETCH HELPERS       |
# ╰───────────────────────────────╯
def fetch_4d_json():
    url = 'https://raw.githubusercontent.com/apiusage/sg-4d-json/main/4d.json'
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        st.error(f"Error fetching 4D JSON: {e}")
        return None

def get_2d():
    nums = fetch_4d_json()
    if not nums:
        return "", ""
    n = str(nums[0]).zfill(4)
    # 1st 2-D
    a, b = (int(n[0]) + int(n[1])) % 10, (int(n[2]) + int(n[3])) % 10
    # 2nd 2-D
    first = sum(int(d) for d in str(int(n[0]) + int(n[1]))) % 10
    second = (int(n[2]) + int(n[3])) % 10
    return f"{a}{b}", f"{first}{second}"

def double_digits_stats(numbers, dates, prize_name):
    st.markdown("### 🔁 Double Digits (e.g., 00, 11 …)")
    dd_df = double_digit_count(numbers, dates)
    st.dataframe(dd_df[['DoubleDigit', 'Frequency']], use_container_width=True)

    sel = st.selectbox(f"Select Double Digit in {prize_name}", dd_df['DoubleDigit'], key=f"dd_{prize_name}")
    recent_dates = dd_df.set_index('DoubleDigit').loc[sel, 'LastDates']
    draw_dates = pd.to_datetime(recent_dates)

    tl_df = pd.DataFrame({
        'DrawDate': draw_dates.strftime('%Y-%m-%d') + ' (' + draw_dates.strftime('%a') + ')'
    })

    tl_df['GapInDays'] = pd.Series(draw_dates.diff()).abs().dt.days.fillna(0).astype(int)
    avg_gap = int(round(tl_df['GapInDays'][1:].mean()))

    avg_row = pd.DataFrame([{'DrawDate': 'Average', 'GapInDays': avg_gap}])
    tl_df_display = pd.concat([avg_row, tl_df], ignore_index=True)

    st.write(tl_df_display.style.apply(
        lambda r: ['background-color: #ffff99' if r.name == 0 else '' for _ in r], axis=1
    ))
# ╭───────────────────────────────╮
# |        PRIZE ANALYSIS         |
# ╰───────────────────────────────╯
def analyze_prize(df, prize_name):
    numbers = df[prize_name].astype(str).str.zfill(4)
    dates = df['DrawDate']

    # most-frequent numbers
    st.markdown(f"### 🏆 Most Frequent {prize_name} Numbers")
    freq_df = numbers.value_counts().reset_index(name='Frequency').rename(columns={'index': 'Number'})
    st.dataframe(freq_df.head(200), use_container_width=True)

    # digit-by-position frequency ★ now uses global TIME_TABS / TIME_DAYS
    st.markdown("### 🔢 Digit-by-Position Frequency (with Time Filters)")
    tabs = st.tabs(TIME_TABS)
    for tab, title in zip(tabs, TIME_TABS):
        with tab:
            filt = df if title == "📊 All" else df[df['DrawDate'] >= df['DrawDate'].max() - pd.Timedelta(days=TIME_DAYS[title])]
            if filt.empty:
                st.warning("No data available for this time range.")
                continue
            nums_f = filt[prize_name].astype(str).str.zfill(4)
            for i in range(4):
                freq = nums_f.str[i].value_counts().sort_index()
                st.plotly_chart(
                    px.bar(x=freq.index, y=freq.values,
                           labels={'x': f'Digit {i+1}', 'y': 'Frequency'},
                           title=f"{title} • Digit {i+1}"),
                    use_container_width=True,
                    key=f"{prize_name}_{title}_pos{i}"
                )

    # double-digit counts
    double_digits_stats(numbers, dates, prize_name)

    # trends
    digit_position_trends_tabs(df, prize_name)
    plot_digit_sum_trend(df, prize_name)

    # high-low / even-odd patterns
    st.markdown("### 🔡 High–Low & Even–Odd Patterns")
    digit_pattern_count_tabs(df, prize_name, 'highlow')
    st.markdown("#### Even-Odd (E = Even, O = Odd)")
    digit_pattern_count_tabs(df, prize_name, 'evenodd')

    st.success(f"✅ Total Numbers Analyzed: {len(numbers)}")

# ╭───────────────────────────────╮
# |        HELPER ROUTINES        |
# ╰───────────────────────────────╯
def double_digit_count(numbers, dates):
    rows = []
    for dd in DOUBLE_DIGITS:
        hits = [d for n, d in zip(numbers, dates) if dd in n]
        if hits:
            rows.append((dd, len(hits), sorted(hits, reverse=True)[:20]))
    return (pd.DataFrame(rows, columns=['DoubleDigit', 'Frequency', 'LastDates'])
              .sort_values('Frequency', ascending=False, ignore_index=True))

def get_digit_pattern(num, mode):
    num = str(num).zfill(4)
    if mode == 'highlow':
        return ''.join('H' if int(d) >= 5 else 'L' for d in num)
    return ''.join('E' if int(d) % 2 == 0 else 'O' for d in num)

def digit_pattern_count(numbers, mode):
    pats = [get_digit_pattern(n, mode) for n in numbers]
    return (pd.DataFrame(Counter(pats).items(), columns=['Pattern', 'Frequency'])
              .sort_values('Frequency', ascending=False))

def digit_pattern_count_tabs(df, prize_name, mode):
    tabs = st.tabs(TIME_TABS)
    for tab, title in zip(tabs, TIME_TABS):
        with tab:
            filt = df if title == "📊 All" else df[df['DrawDate'] >= pd.Timestamp.today() - pd.Timedelta(days=TIME_DAYS[title])]
            if filt.empty:
                st.warning("No data for this range.")
                continue
            patt_df = digit_pattern_count(filt[prize_name].astype(str).str.zfill(4), mode)
            st.dataframe(patt_df, use_container_width=True)
            st.bar_chart(patt_df.set_index('Pattern')['Frequency'])

def digit_position_trends_tabs(df, prize_name):
    st.markdown("### 📈 Digit Position Trends")
    tabs = st.tabs(TREND_TABS)
    for tab, title in zip(tabs, TREND_TABS):
        with tab:
            filt = df[df['DrawDate'] >= pd.Timestamp.today() - pd.Timedelta(days=TREND_DAYS[title])].sort_values('DrawDate')
            if filt.empty:
                st.warning(f"No data for {title}.")
                continue
            nums = filt[prize_name].astype(str).str.zfill(4).tolist()
            cols = {f'Digit {i+1}': [int(n[i]) for n in nums] for i in range(4)}
            for label, series in cols.items():
                st.info(label)
                st.line_chart(pd.DataFrame({label: series}))

def plot_digit_sum_trend(df, prize_name):
    st.markdown(f"### ➕ Digit Sum Trend ({prize_name})")
    tabs = st.tabs(TREND_TABS)
    for tab, title in zip(tabs, TREND_TABS):
        with tab:
            filt = df[df['DrawDate'] >= pd.Timestamp.today() - pd.Timedelta(days=TREND_DAYS[title])].sort_values('DrawDate')
            if filt.empty:
                st.warning("No data for this range.")
                continue
            nums = filt[prize_name].astype(str).str.zfill(4)
            sums = nums.apply(lambda x: sum(map(int, x)))
            chart_df = pd.DataFrame({'DrawDate': filt['DrawDate'], 'DigitSum': sums})
            st.plotly_chart(
                px.line(chart_df, x='DrawDate', y='DigitSum',
                        title=f"{title} • Digit Sum Trend",
                        labels={'DrawDate': 'Draw Date', 'DigitSum': 'Sum'}),
                use_container_width=True)
            stats = chart_df['DigitSum'].agg(['mean', 'max', 'min', 'std']).round(2)
            st.dataframe(stats.rename({'mean': 'Average', 'std': 'Std Dev'}).to_frame('Value'))

def prize_digit_breakdown(df, prize_name):
    st.markdown(f"### 🔢 Digit Frequency per {prize_name} Prize (Latest 100)")

    recent = (df[['DrawDate', prize_name]].dropna()
              .sort_values('DrawDate', ascending=False)
              .head(100)
              .reset_index(drop=True))  # <-- Reset index here

    recent[prize_name] = recent[prize_name].astype(str).str.zfill(4)

    digit_cols = list(map(str, range(10)))
    freq = [[num.count(str(d)) for d in range(10)] for num in recent[prize_name]]
    summary_df = pd.DataFrame(freq, columns=digit_cols)
    summary_df.insert(0, 'Number', recent[prize_name])  # This will now align properly

    # Add average row
    avg = summary_df[digit_cols].mean().round(3)
    avg_row = pd.DataFrame([['Average', *avg.tolist()]], columns=['Number'] + digit_cols)
    summary_df = pd.concat([avg_row, summary_df], ignore_index=True)

    def highlight_nonzero(v):
        try:
            return 'background-color: yellow' if float(v) > 0 else ''
        except:
            return ''

    def highlight_average(row):
        return ['background-color: lightblue; font-weight:bold'] * len(row) if row['Number'] == 'Average' else [''] * len(row)

    styled_df = (
        summary_df.style
        .apply(highlight_average, axis=1)
        .map(highlight_nonzero, subset=pd.IndexSlice[1:, digit_cols])
        .format({col: "{:.3f}" for col in digit_cols}, subset=pd.IndexSlice[[0], digit_cols])
        .format({col: "{:.0f}" for col in digit_cols}, subset=pd.IndexSlice[1:, digit_cols])
        .set_properties(subset=summary_df.columns, **{'text-align': 'center'})
    )

    st.dataframe(styled_df, use_container_width=True)

# ╭───────────────────────────────╮
# |        (OPTIONAL) ML          |
# ╰───────────────────────────────╯
def predict_next_number(df, prize_name):
    st.markdown("### 🤖 ML Predictions for Next Likely Number")
    df = df.sort_values('DrawDate')
    nums = df[prize_name].astype(str).str.zfill(4)

    feats, targets = [], []
    for cur, nxt in zip(nums[:-1], nums[1:]):
        feats.append([int(cur[i]) for i in range(4)] +
                     [sum(int(d)>=5 for d in cur), sum(int(d)%2==0 for d in cur)])
        targets.append(nxt)

    if len(feats) < 10:
        st.warning("Not enough data to train ML models.")
        return

    le = LabelEncoder()
    y = le.fit_transform(targets)
    X_tr, X_te, y_tr, y_te = train_test_split(feats, y, test_size=0.2, random_state=42)

    rf = RandomForestClassifier(n_estimators=100, random_state=42).fit(X_tr, y_tr)
    knn = KNeighborsClassifier(n_neighbors=3).fit(X_tr, y_tr)

    last = nums.iloc[-1]
    last_feat = [[int(last[i]) for i in range(4)] +
                 [sum(int(d)>=5 for d in last), sum(int(d)%2==0 for d in last)]]

    st.info(f"📌 Last {prize_name}: **{last}**")
    st.success(f"🔮 RF Prediction: **{le.inverse_transform(rf.predict(last_feat))[0]}**")
    st.success(f"🔮 KNN Prediction: **{le.inverse_transform(knn.predict(last_feat))[0]}**")


def predict_4d_digit_sums_xgboost():
    df = pd.read_csv("https://raw.githubusercontent.com/apiusage/sg-4d-json/refs/heads/main/4d_results.csv")

    digit_sum = lambda n: sum(map(int, str(n).zfill(4)))
    entries = [{'date': row['DrawDate'], 'digit_sum': digit_sum(row[col])}
               for _, row in df.iterrows() for col in ['1st', '2nd', '3rd'] if str(row[col]).isdigit()]

    data = pd.DataFrame(entries)
    data['date'] = pd.to_datetime(data['date'], errors='coerce')
    data.dropna(subset=['date'], inplace=True)
    data[['year', 'month', 'day', 'weekday']] = data['date'].apply(lambda d: pd.Series([d.year, d.month, d.day, d.weekday()]))

    X = data[['year', 'month', 'day', 'weekday']]
    y = data['digit_sum']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(objective='multi:softprob', num_class=37, eval_metric='mlogloss', use_label_encoder=False)
    model.fit(X_train, y_train)
    st.success(f"🏆 Top 5 Predicted Digit Sums - Accuracy: {accuracy_score(y_test, model.predict(X_test)) * 100:.2f}%")

    latest = data.iloc[-1]
    next_inp = pd.DataFrame([{
        'year': latest.year,
        'month': latest.month,
        'day': (latest.day % 28) + 1,
        'weekday': (latest.weekday + 1) % 7
    }])

    probs = model.predict_proba(next_inp)[0]
    top5 = sorted(enumerate(probs), key=lambda x: -x[1])[:5]

    for ds, p in top5:
        st.write(f"**Digit Sum:** {ds:2} ({p*100:.2f}%)")


# ╭───────────────────────────────╮
# |         LAUNCH APP            |
# ╰───────────────────────────────╯
if __name__ == "__main__":
    run_setAnalysis()

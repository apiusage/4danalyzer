import streamlit as st
import pandas as pd

def run_WinningCalculator():
    st.set_page_config(page_title="Win How Much?", page_icon="💰", layout="centered")

    # Title banner
    st.markdown(
        """
        <div style="background-color:#464e5f;padding:2px;border-radius:15px;text-align:center;">
            <h1 style="color:white;">💰 Win How Much? 💰</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ✅ Responsive CSS (columns + table)
    st.markdown(
        """
        <style>
        /* Stack columns on small screens */
        @media (max-width: 600px) {
            div[data-testid="column"] {
                width: 100% !important;
                flex: unset !important;
            }
        }
        /* Make table scrollable horizontally */
        .responsive-table {
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        th, td {
            padding: 6px 8px;
            text-align: center;
            border: 1px solid #ddd;
            white-space: nowrap;
        }
        th {
            background-color: #464e5f;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Input fields
    col1, col2 = st.columns(2)
    with col1:
        big_bet = st.number_input("💵 Big Bet", min_value=0, value=0, step=1)
    with col2:
        small_bet = st.number_input("💵 Small Bet", min_value=0, value=0, step=1)

    # Prize structure
    prizes = {
        "First": {"Big Prize": 2000, "Small Prize": 3000},
        "Second": {"Big Prize": 1000, "Small Prize": 2000},
        "Third": {"Big Prize": 490, "Small Prize": 800},
        "Starter": {"Big Prize": 250, "Small Prize": None},
        "Consolation": {"Big Prize": 60, "Small Prize": None},
    }

    # Build result table
    rows = []
    for category, prize in prizes.items():
        big_prize = prize["Big Prize"]
        small_prize = prize["Small Prize"]

        big_actual = big_bet * big_prize if big_prize else 0
        small_actual = small_bet * small_prize if small_prize else 0
        row_total = big_actual + small_actual

        rows.append({
            "Category": category,
            "Total": f"<span style='font-weight:bold; color:green;'>${row_total:,}</span>"
                      if row_total > 0 else f"${row_total:,}",
            "Big Prize": f"${big_prize:,}" if big_prize else "•",
            "Big Bet": f"${big_bet:,}",
            "Big Actual": f"${big_actual:,}",
            "Small Prize": f"${small_prize:,}" if small_prize else "•",
            "Small Bet": f"${small_bet:,}",
            "Small Actual": f"${small_actual:,}",
        })

    df = pd.DataFrame(rows)

    # ✅ Remove the left numbering column
    df = df.reset_index(drop=True)

    # ✅ Wrap table in scrollable div
    st.markdown(
        f"""
        <div class="responsive-table">
            {df.to_html(escape=False, index=False)}
        </div>
        """,
        unsafe_allow_html=True,
    )

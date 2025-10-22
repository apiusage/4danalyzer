import pandas as pd
from collections import Counter, defaultdict
import itertools
import math
import random

# ---------- CONFIG ----------
CSV_URL = "https://raw.githubusercontent.com/apiusage/sg-4d-json/main/4d_results_all.csv"
TOP_N = 10
DECAY_HALF_LIFE_DAYS = 90.0
PRIZE_WEIGHTS = {
    "1st": 1.0,
    "2nd": 0.9,
    "3rd": 0.8,
    "Starter": 0.5,
    "Consolation": 0.3
}
WEIGHTS = {
    "freq": 0.35,
    "pos":  0.30,
    "recency": 0.15,
    "balance": 0.10,
    "streak": 0.05,
    "rand": 0.05
}
# ----------------------------

def predict_4d_numbers(top_n=TOP_N, csv_url=CSV_URL):
    """Fetch 4D results CSV, compute stats, and return top predicted 4D numbers."""
    
    # ---------- READ CSV ----------
    def read_draws(file_path):
        df = pd.read_csv(file_path)
        records = []
        for idx, row in df.iterrows():
            # Extract date inside parentheses
            raw_date = str(row['DrawDate'])
            if '(' in raw_date and ')' in raw_date:
                date_str = raw_date.split('(')[1].split(')')[0]
            else:
                date_str = raw_date
            date = pd.to_datetime(date_str, errors='coerce')
            if pd.isna(date):
                continue

            for prize_type in ['1st', '2nd', '3rd']:
                num = str(row[prize_type]).zfill(4)
                records.append((date, prize_type, num))
            for i in range(10):
                col = f'Starter{i+1}'
                if col in row and not pd.isna(row[col]):
                    num = str(row[col]).zfill(4)
                    records.append((date, 'Starter', num))
            for i in range(10):
                col = f'Consolation{i+1}'
                if col in row and not pd.isna(row[col]):
                    num = str(row[col]).zfill(4)
                    records.append((date, 'Consolation', num))
        records.sort(key=lambda x: x[0])
        return records

    # ---------- STATS ----------
    def compute_stats(records):
        full_freq = Counter()
        pos_freq = [Counter() for _ in range(4)]
        recency_score = defaultdict(float)
        last_seen_index = {}
        streaks = defaultdict(int)
        today = records[-1][0] if records else pd.Timestamp.now()

        for idx, (date, prize_type, num) in enumerate(records):
            weight = PRIZE_WEIGHTS.get(prize_type, 0.5)
            full_freq[num] += weight
            for p, d in enumerate(num):
                pos_freq[p][d] += weight
            days_ago = (today - date).days
            w = weight * (0.5 ** (days_ago / DECAY_HALF_LIFE_DAYS))
            recency_score[num] += w
            if idx > 0 and records[idx-1][2] == num:
                streaks[num] += 1
            last_seen_index[num] = idx
        return full_freq, pos_freq, recency_score, last_seen_index, streaks

    # ---------- NORMALIZATION ----------
    def normalize_dict_vals(d):
        if not d:
            return {}
        vals = list(d.values())
        mn, mx = min(vals), max(vals)
        out = {}
        if mx == mn:
            for k in d: out[k] = 1.0
            return out
        for k,v in d.items():
            out[k] = (v - mn) / (mx - mn)
        return out

    # ---------- FEATURE FUNCTIONS ----------
    def digit_position_score(num, pos_freq):
        s = 1.0
        for p,d in enumerate(num):
            total = sum(pos_freq[p].values()) or 1
            s *= (pos_freq[p].get(d,0) / total)
        return s

    def balance_score(num):
        digits = [int(d) for d in num]
        odd = sum(d%2 for d in digits)
        even = 4 - odd
        odd_even_balance = 1.0 - (abs(odd-even)/4.0)
        high = sum(1 for d in digits if d>=5)
        high_low_balance = 1.0 - (abs(high-(4-high))/4.0)
        return (odd_even_balance + high_low_balance)/2.0

    # ---------- CANDIDATES ----------
    def build_candidates(records, full_freq, pos_freq, last_seen_index, streaks, top_limit=10000):
        seen_numbers = set(full_freq.keys())
        candidates = set(seen_numbers)
        for p in range(4):
            top_digits = [d for d,_ in pos_freq[p].most_common(5)] or [str(i) for i in range(10)]
            if p==0:
                combos = [[d] for d in top_digits]
            else:
                combos = [c+[d] for c in combos for d in top_digits]
        for c in combos:
            candidates.add(''.join(c))
        candidates = list(candidates)[:top_limit]
        return candidates

    # ---------- SCORING ----------
    def score_candidates(candidates, full_freq, pos_freq, recency_score, last_seen_index, streaks, total_records):
        norm_full = normalize_dict_vals(full_freq)
        norm_recency = normalize_dict_vals(recency_score)
        scores = {}
        for num in candidates:
            f_full = norm_full.get(num,0.0)
            f_pos_raw = digit_position_score(num,pos_freq)
            f_pos = math.log1p(f_pos_raw) if f_pos_raw>0 else 0.0
            f_rec = norm_recency.get(num,0.0)
            f_bal = balance_score(num)
            f_streak = streaks.get(num,0)/ (1 + max(1, max(streaks.values()) if streaks else 1))
            sc = (
                WEIGHTS["freq"] * f_full +
                WEIGHTS["pos"]  * f_pos +
                WEIGHTS["recency"] * f_rec +
                WEIGHTS["balance"] * f_bal +
                WEIGHTS["streak"] * f_streak +
                WEIGHTS["rand"] * random.uniform(0,0.05)
            )
            scores[num] = sc
        ranked = sorted(scores.items(), key=lambda x:x[1], reverse=True)
        return ranked

    # ---------- MAIN LOGIC ----------
    records = read_draws(csv_url)
    if not records:
        return []
    full_freq, pos_freq, recency_score, last_seen_index, streaks = compute_stats(records)
    candidates = build_candidates(records, full_freq, pos_freq, last_seen_index, streaks, top_limit=8000)
    ranked = score_candidates(candidates, full_freq, pos_freq, recency_score, last_seen_index, streaks, len(records))
    
    return ranked[:top_n]  # Return top N numbers with scores

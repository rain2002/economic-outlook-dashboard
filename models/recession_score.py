import pandas as pd
import numpy as np

def load_features():
    return pd.read_csv("raw_data/features_monthly.csv", index_col="obs_date", parse_dates=True)

def logistic(x):
    return 1 / (1 + np.exp(-x))

WEIGHTS = {
    "yield_curve_spread_zscore": -0.30,   # inverted (negative) = higher risk
    "sahm_rule": 0.25,                     # already 0/1-ish scale, direct signal
    "credit_spread_zscore": 0.20,          # wider spread = higher risk
    "consumer_sentiment_zscore": -0.10,    # low sentiment = higher risk
    "industrial_production_zscore": -0.10, # falling production = higher risk
    "housing_starts_zscore": -0.05,        # falling starts = higher risk
}

def compute_score(df):
    df = df.copy()
    df["sahm_scaled"] = (df["sahm_rule"] / 0.5).clip(0, 2)  # 0.5 = official trigger threshold

    raw_score = (
        -1.2 * df["yield_curve_spread_zscore"].fillna(0) +
        2.5 * df["sahm_scaled"].fillna(0) - 1.0 +   # centers below 0 when sahm is low
        0.8 * df["credit_spread_zscore"].fillna(0) +
        -0.5 * df["consumer_sentiment_zscore"].fillna(0) +
        -0.5 * df["industrial_production_zscore"].fillna(0) +
        -0.3 * df["housing_starts_zscore"].fillna(0) -
        1.0  # bias term shifts baseline down since these are historically low-risk signals
    )
    df["recession_probability"] = logistic(raw_score) * 100
    return df[["yield_curve_spread", "sahm_rule", "credit_spread", "recession_probability"]]

if __name__ == "__main__":
    df = load_features()
    result = compute_score(df)
    result.to_csv("raw_data/recession_score.csv")
    print(result.tail(12))
    print(f"\nCurrent recession probability: {result['recession_probability'].iloc[-1]:.1f}%")
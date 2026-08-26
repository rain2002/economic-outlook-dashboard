import os
import pandas as pd
from fredapi import Fred
from dotenv import load_dotenv

load_dotenv()
fred = Fred(api_key=os.getenv("FRED_API_KEY"))

SERIES = {
    "T10Y3M": "yield_curve_spread",
    "BAA10Y": "credit_spread",
    "UNRATE": "unemployment_rate",
    "SAHMREALTIME": "sahm_rule",
    "CPIAUCSL": "cpi_headline",
    "PCEPILFE": "core_pce",
    "UMCSENT": "consumer_sentiment",
    "INDPRO": "industrial_production",
    "HOUST": "housing_starts",
    "GDPC1": "real_gdp",
}

START_DATE = "2000-01-01"

def fetch_all_series():
    frames = []
    for series_id, label in SERIES.items():
        data = fred.get_series(series_id, observation_start=START_DATE)
        df = data.reset_index()
        df.columns = ["date", "value"]
        df["series_id"] = series_id
        df["indicator"] = label
        frames.append(df)
        print(f"Fetched {series_id} ({label}): {len(df)} rows")
    return pd.concat(frames, ignore_index=True)

if __name__ == "__main__":
    combined = fetch_all_series()
    os.makedirs("raw_data", exist_ok=True)
    combined.to_csv("raw_data/fred_raw.csv", index=False)
    print(f"Saved {len(combined)} total rows to raw_data/fred_raw.csv")
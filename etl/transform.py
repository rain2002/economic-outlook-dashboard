import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def load_all(conn):
    query = """
        SELECT i.indicator_name, f.obs_date, f.value
        FROM fact_observations f
        JOIN dim_indicator i ON f.indicator_id = i.indicator_id
        ORDER BY i.indicator_name, f.obs_date
    """
    return pd.read_sql(query, conn)

def resample_monthly(df):
    pivot = df.pivot(index="obs_date", columns="indicator_name", values="value")
    pivot.index = pd.to_datetime(pivot.index)
    monthly = pivot.resample("MS").mean()
    monthly["real_gdp"] = monthly["real_gdp"].ffill()
    return monthly

def engineer_features(monthly):
    df = monthly.copy()
    for col in ["unemployment_rate", "cpi_headline", "core_pce", "consumer_sentiment",
                "industrial_production", "housing_starts", "yield_curve_spread", "credit_spread"]:
        df[f"{col}_3m_avg"] = df[col].rolling(3).mean()
        df[f"{col}_12m_avg"] = df[col].rolling(12).mean()
        df[f"{col}_zscore"] = (df[col] - df[col].rolling(60).mean()) / df[col].rolling(60).std()

    df["cpi_yoy"] = df["cpi_headline"].pct_change(12) * 100
    df["core_pce_yoy"] = df["core_pce"].pct_change(12) * 100
    df["yield_curve_inverted"] = (df["yield_curve_spread"] < 0).astype(int)
    df["recession_flag_sahm"] = (df["sahm_rule"] >= 0.5).astype(int)
    return df

if __name__ == "__main__":
    conn = get_conn()
    raw = load_all(conn)
    monthly = resample_monthly(raw)
    features = engineer_features(monthly)
    os.makedirs("raw_data", exist_ok=True)
    features = features.dropna(subset=["unemployment_rate"])
    features.to_csv("raw_data/features_monthly.csv")
    print(f"Saved {features.shape[0]} rows x {features.shape[1]} columns")
    print(features.tail(3))
    conn.close()
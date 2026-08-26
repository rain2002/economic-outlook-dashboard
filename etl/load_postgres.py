import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

DOMAIN_MAP = {
    "T10Y3M": ("yield_curve_spread", "Rates", "Daily"),
    "BAA10Y": ("credit_spread", "Credit", "Daily"),
    "UNRATE": ("unemployment_rate", "Labor", "Monthly"),
    "SAHMREALTIME": ("sahm_rule", "Labor", "Monthly"),
    "CPIAUCSL": ("cpi_headline", "Prices", "Monthly"),
    "PCEPILFE": ("core_pce", "Prices", "Monthly"),
    "UMCSENT": ("consumer_sentiment", "Consumer", "Monthly"),
    "INDPRO": ("industrial_production", "Manufacturing", "Monthly"),
    "HOUST": ("housing_starts", "Housing", "Monthly"),
    "GDPC1": ("real_gdp", "Output", "Quarterly"),
}

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def load_dim_indicator(conn):
    cur = conn.cursor()
    rows = [(sid, name, domain, freq) for sid, (name, domain, freq) in DOMAIN_MAP.items()]
    execute_values(
        cur,
        """INSERT INTO dim_indicator (series_id, indicator_name, domain, frequency)
           VALUES %s ON CONFLICT (series_id) DO NOTHING""",
        rows
    )
    conn.commit()
    cur.close()

def load_fact_observations(conn, df):
    cur = conn.cursor()
    cur.execute("SELECT indicator_id, series_id FROM dim_indicator")
    id_map = {series_id: iid for iid, series_id in cur.fetchall()}

    df = df.dropna(subset=["value"])
    rows = [
        (id_map[row.series_id], row.date, row.value)
        for row in df.itertuples()
        if row.series_id in id_map
    ]

    execute_values(
        cur,
        """INSERT INTO fact_observations (indicator_id, obs_date, value)
           VALUES %s ON CONFLICT (indicator_id, obs_date) DO UPDATE SET value = EXCLUDED.value""",
        rows
    )
    conn.commit()
    cur.close()
    print(f"Loaded {len(rows)} observations")

if __name__ == "__main__":
    df = pd.read_csv("raw_data/fred_raw.csv", parse_dates=["date"])
    conn = get_conn()
    load_dim_indicator(conn)
    load_fact_observations(conn, df)
    conn.close()
    print("Done.")
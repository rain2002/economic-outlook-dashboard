import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def load_monthly_features(conn):
    df = pd.read_csv("raw_data/features_monthly.csv", parse_dates=["obs_date"])
    cols = ["obs_date","unemployment_rate","cpi_headline","cpi_yoy","core_pce","core_pce_yoy",
            "consumer_sentiment","industrial_production","housing_starts","real_gdp",
            "yield_curve_spread","credit_spread","sahm_rule","yield_curve_inverted","recession_flag_sahm"]
    df = df[cols].where(pd.notnull(df[cols]), None)
    rows = [tuple(r) for r in df.itertuples(index=False)]
    cur = conn.cursor()
    execute_values(cur, f"""INSERT INTO monthly_features ({",".join(cols)}) VALUES %s
        ON CONFLICT (obs_date) DO UPDATE SET
        {",".join(f"{c}=EXCLUDED.{c}" for c in cols if c != "obs_date")}""", rows)
    conn.commit()
    cur.close()
    print(f"Loaded {len(rows)} monthly_features rows")

def load_forecasts(conn):
    files = {
        "real_gdp": "raw_data/forecast_arima_real_gdp.csv",
        "unemployment_rate": "raw_data/forecast_arima_unemployment_rate.csv",
        "cpi_yoy": "raw_data/forecast_arima_cpi_yoy.csv",
    }
    forecast_dates = pd.date_range(start="2026-07-01", periods=18, freq="MS")
    cur = conn.cursor()
    total = 0
    for indicator, path in files.items():
        df = pd.read_csv(path)
        df = df.iloc[:, 1:]  # drop the bad integer index column
        df.columns = ["forecast_value", "lower_80", "upper_80"]
        df["forecast_date"] = forecast_dates[:len(df)]
        rows = [(row.forecast_date, indicator, "ARIMA", row.forecast_value, row.lower_80, row.upper_80)
                for row in df.itertuples(index=False)]
        execute_values(cur, """INSERT INTO forecast_results
            (forecast_date, indicator, model, forecast_value, lower_80, upper_80) VALUES %s
            ON CONFLICT (forecast_date, indicator, model) DO UPDATE SET
            forecast_value=EXCLUDED.forecast_value, lower_80=EXCLUDED.lower_80, upper_80=EXCLUDED.upper_80""", rows)
        total += len(rows)
    conn.commit()
    cur.close()
    print(f"Loaded {total} forecast rows")

def load_recession_scores(conn):
    df = pd.read_csv("raw_data/recession_score.csv", parse_dates=["obs_date"])
    rows = [tuple(r) for r in df.itertuples(index=False)]
    cur = conn.cursor()
    execute_values(cur, """INSERT INTO recession_scores
        (obs_date, yield_curve_spread, sahm_rule, credit_spread, recession_probability) VALUES %s
        ON CONFLICT (obs_date) DO UPDATE SET
        recession_probability=EXCLUDED.recession_probability""", rows)
    conn.commit()
    cur.close()
    print(f"Loaded {len(rows)} recession_score rows")

if __name__ == "__main__":
    conn = get_conn()
    load_monthly_features(conn)
    load_forecasts(conn)
    load_recession_scores(conn)
    conn.close()
    print("Done.")
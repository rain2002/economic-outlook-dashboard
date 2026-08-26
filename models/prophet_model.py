import pandas as pd
from prophet import Prophet
import warnings
warnings.filterwarnings("ignore")

TARGETS = ["real_gdp", "unemployment_rate", "cpi_yoy"]
FORECAST_MONTHS = 18

def load_features():
    df = pd.read_csv("raw_data/features_monthly.csv", index_col="obs_date", parse_dates=True)
    return df

def run_prophet(df, col):
    series = df[[col]].dropna().reset_index()
    series.columns = ["ds", "y"]
    model = Prophet(interval_width=0.80)
    model.fit(series)
    future = model.make_future_dataframe(periods=FORECAST_MONTHS, freq="MS")
    forecast = model.predict(future)
    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(FORECAST_MONTHS)
    result.columns = ["date", "forecast", "lower_80", "upper_80"]
    return result.set_index("date")

if __name__ == "__main__":
    df = load_features()
    for col in TARGETS:
        res = run_prophet(df, col)
        print(f"\n=== {col} forecast (Prophet) ===")
        print(res.tail(6))
        res.to_csv(f"raw_data/forecast_prophet_{col}.csv")
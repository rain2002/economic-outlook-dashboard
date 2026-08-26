import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")

TARGETS = {
    "real_gdp": (1, 1, 1),
    "unemployment_rate": (2, 1, 2),
    "cpi_yoy": (2, 1, 2),
}

FORECAST_MONTHS = 18  # June 2026 -> Dec 2027

def load_features():
    df = pd.read_csv("raw_data/features_monthly.csv", index_col="obs_date", parse_dates=True)
    return df

def run_arima(df, col, order, trend="t"):
    series = df[col].dropna()
    series.index = pd.DatetimeIndex(series.index).to_period("M").to_timestamp()
    series = series.asfreq("MS")
    model = ARIMA(series, order=order, trend=trend)
    fit = model.fit()
    forecast = fit.get_forecast(steps=FORECAST_MONTHS)
    mean = forecast.predicted_mean
    ci = forecast.conf_int(alpha=0.20)
    result = pd.DataFrame({
        "forecast": mean,
        "lower_80": ci.iloc[:, 0],
        "upper_80": ci.iloc[:, 1],
    })
    return result

if __name__ == "__main__":
    df = load_features()
    all_results = {}
    for col, order in TARGETS.items():
        res = run_arima(df, col, order)
        all_results[col] = res
        print(f"\n=== {col} forecast (ARIMA{order}) ===")
        print(res.tail(6))
        res.to_csv(f"raw_data/forecast_arima_{col}.csv")
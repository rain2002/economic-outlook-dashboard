import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import warnings
warnings.filterwarnings("ignore")

TARGETS = {
    "real_gdp": (1, 1, 1),
    "unemployment_rate": (2, 1, 2),
    "cpi_yoy": (2, 1, 2),
}

CUTOFF = "2024-12-01"

def load_features():
    df = pd.read_csv("raw_data/features_monthly.csv", index_col="obs_date", parse_dates=True)
    return df

def backtest_arima(df, col, order, cutoff):
    series = df[col].dropna()
    train = series[series.index <= cutoff]
    test = series[series.index > cutoff]
    if len(test) == 0:
        return None
    model = ARIMA(train, order=order, trend="t")
    fit = model.fit()
    forecast = fit.get_forecast(steps=len(test))
    pred = forecast.predicted_mean
    pred.index = test.index
    return test, pred

def backtest_prophet(df, col, cutoff):
    series = df[[col]].dropna().reset_index()
    series.columns = ["ds", "y"]
    train = series[series["ds"] <= cutoff]
    test = series[series["ds"] > cutoff]
    if len(test) == 0:
        return None
    model = Prophet(interval_width=0.80)
    model.fit(train)
    future = model.make_future_dataframe(periods=len(test), freq="MS")
    forecast = model.predict(future)
    merged = test.merge(forecast[["ds", "yhat"]], on="ds", how="left")
    merged = merged.dropna(subset=["yhat"])
    return merged.set_index("ds")["y"], merged.set_index("ds")["yhat"]

def rmse(actual, pred):
    return np.sqrt(np.mean((actual.values - pred.values) ** 2))

def mape(actual, pred):
    return np.mean(np.abs((actual.values - pred.values) / actual.values)) * 100

if __name__ == "__main__":
    df = load_features()
    results = []
    for col, order in TARGETS.items():
        a_test, a_pred = backtest_arima(df, col, order, CUTOFF)
        p_test, p_pred = backtest_prophet(df, col, CUTOFF)

        a_rmse, a_mape = rmse(a_test, a_pred), mape(a_test, a_pred)
        p_rmse, p_mape = rmse(p_test, p_pred), mape(p_test, p_pred)

        results.append({"indicator": col, "arima_rmse": a_rmse, "arima_mape": a_mape,
                         "prophet_rmse": p_rmse, "prophet_mape": p_mape,
                         "winner": "ARIMA" if (not np.isnan(p_rmse) and a_rmse < p_rmse) or np.isnan(p_rmse) else "Prophet"})

        print(f"\n=== {col} backtest (train<=2024-12, test=2025+) ===")
        print(f"ARIMA   RMSE={a_rmse:.4f}  MAPE={a_mape:.2f}%")
        print(f"Prophet RMSE={p_rmse:.4f}  MAPE={p_mape:.2f}%")
        print(f"Winner: {results[-1]['winner']}")

    pd.DataFrame(results).to_csv("raw_data/backtest_results.csv", index=False)
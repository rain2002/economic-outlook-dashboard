# US Economic Outlook Dashboard

A Power BI dashboard tracking historical and forecast US macroeconomic indicators through 2027, with a recession risk monitor built from real-time KPI signals.

## Data Source

PostgreSQL database with four core views:

| View | Description |
|---|---|
| `vw_2027_outlook` | Forecast values by indicator with 80% confidence bands (`lower_80`, `upper_80`) |
| `vw_historical_vs_forecast` | Time series of actual vs. forecast values by indicator and date, tagged via `data_type` |
| `vw_kpi_latest` | Latest snapshot of macro KPIs: real GDP, CPI YoY, core PCE YoY, consumer sentiment, housing starts, industrial production, credit spread, Sahm Rule |
| `vw_recession_risk` | Historical recession probability, Sahm Rule value, yield curve spread, and credit spread by date |

## Report Structure

### Page 1 — Executive Summary
- Card: 2027 Real GDP forecast (filtered from `vw_2027_outlook`)
- Card: 2027 Unemployment Rate forecast
- Card: 2027 CPI YoY forecast
- Gauge: Current Recession Probability (0–100 scale, target line at 30)

### Page 2 — Trends
- Line chart: Real GDP — Historical vs. Forecast
- Line chart: CPI YoY — Historical vs. Forecast
- Line chart: Unemployment Rate — Historical vs. Forecast

All three charts split by `data_type` (Actual / Forecast) via Legend, filtered to a single `indicator` value each. Y-axis aggregation set to **Average** (not Sum) to avoid double-counting where multiple rows exist per date.

### Page 3 — KPI & Risk Details
- Table: Latest Economic KPIs (single-row snapshot from `vw_kpi_latest`)
- Table: Recession Risk Indicators — History, sorted by date descending, with conditional background-color formatting on `recession_probability` and `sahm_rule`

## Key DAX Measure

```dax
Current Recession Probability = 
CALCULATE(
    SELECTEDVALUE('public vw_recession_risk'[recession_probability]),
    FILTER('public vw_recession_risk', 'public vw_recession_risk'[date] = MAX('public vw_recession_risk'[date]))
)
```

## Data Model Notes

- Storage mode: **Import**
- A relationship between `vw_historical_vs_forecast` and `vw_2027_outlook` on `indicator` was kept (legitimate shared key).
- An auto-detected relationship between `vw_recession_risk` and `vw_kpi_latest` was removed — no real shared key existed between them.
- Source database runs on `localhost:5432`, so scheduled refresh in Power BI Service requires either an On-premises Data Gateway or migrating to a cloud-hosted Postgres instance (e.g. Neon, Supabase).

## Status

Published to Power BI Service ("My workspace") as `economic_outlook` (Report + Semantic model). Scheduled refresh pending gateway/cloud migration decision.

## Files

- `.pbix` file to be added — export from Power BI Desktop
- SQL view definitions to be added

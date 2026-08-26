-- Combined historical + forecast view for GDP, unemployment, CPI (for Power BI trend charts)
CREATE OR REPLACE VIEW vw_historical_vs_forecast AS
SELECT
    obs_date AS date,
    'real_gdp' AS indicator,
    real_gdp AS value,
    NULL::numeric AS lower_80,
    NULL::numeric AS upper_80,
    'Actual' AS data_type
FROM monthly_features WHERE real_gdp IS NOT NULL
UNION ALL
SELECT obs_date, 'unemployment_rate', unemployment_rate, NULL, NULL, 'Actual'
FROM monthly_features WHERE unemployment_rate IS NOT NULL
UNION ALL
SELECT obs_date, 'cpi_yoy', cpi_yoy, NULL, NULL, 'Actual'
FROM monthly_features WHERE cpi_yoy IS NOT NULL
UNION ALL
SELECT forecast_date, indicator, forecast_value, lower_80, upper_80, 'Forecast'
FROM forecast_results WHERE model = 'ARIMA';

-- KPI summary — latest values across all 8 domains, for dashboard cards
CREATE OR REPLACE VIEW vw_kpi_latest AS
SELECT
    obs_date AS as_of_date,
    unemployment_rate, cpi_yoy, core_pce_yoy, consumer_sentiment,
    industrial_production, housing_starts, real_gdp,
    yield_curve_spread, credit_spread, sahm_rule
FROM monthly_features
ORDER BY obs_date DESC
LIMIT 1;

-- Recession risk trend, for gauge/line chart
CREATE OR REPLACE VIEW vw_recession_risk AS
SELECT obs_date AS date, recession_probability, yield_curve_spread, sahm_rule, credit_spread
FROM recession_scores
ORDER BY obs_date;

-- 2027 outlook summary — final headline numbers for exec dashboard
CREATE OR REPLACE VIEW vw_2027_outlook AS
SELECT indicator, forecast_value, lower_80, upper_80
FROM forecast_results
WHERE forecast_date = '2027-12-01' AND model = 'ARIMA';
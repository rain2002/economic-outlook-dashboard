CREATE TABLE monthly_features (
    obs_date DATE PRIMARY KEY,
    unemployment_rate NUMERIC,
    cpi_headline NUMERIC,
    cpi_yoy NUMERIC,
    core_pce NUMERIC,
    core_pce_yoy NUMERIC,
    consumer_sentiment NUMERIC,
    industrial_production NUMERIC,
    housing_starts NUMERIC,
    real_gdp NUMERIC,
    yield_curve_spread NUMERIC,
    credit_spread NUMERIC,
    sahm_rule NUMERIC,
    yield_curve_inverted INT,
    recession_flag_sahm INT
);

CREATE TABLE forecast_results (
    forecast_date DATE,
    indicator VARCHAR(30),
    model VARCHAR(20),
    forecast_value NUMERIC,
    lower_80 NUMERIC,
    upper_80 NUMERIC,
    PRIMARY KEY (forecast_date, indicator, model)
);

CREATE TABLE recession_scores (
    obs_date DATE PRIMARY KEY,
    yield_curve_spread NUMERIC,
    sahm_rule NUMERIC,
    credit_spread NUMERIC,
    recession_probability NUMERIC
);
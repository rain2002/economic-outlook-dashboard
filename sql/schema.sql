CREATE TABLE dim_indicator (
    indicator_id SERIAL PRIMARY KEY,
    series_id VARCHAR(20) UNIQUE NOT NULL,
    indicator_name VARCHAR(50) NOT NULL,
    domain VARCHAR(30),
    frequency VARCHAR(10),
    source VARCHAR(30) DEFAULT 'FRED'
);

CREATE TABLE fact_observations (
    obs_id SERIAL PRIMARY KEY,
    indicator_id INT REFERENCES dim_indicator(indicator_id),
    obs_date DATE NOT NULL,
    value NUMERIC,
    UNIQUE(indicator_id, obs_date)
);

CREATE INDEX idx_fact_date ON fact_observations(obs_date);
CREATE INDEX idx_fact_indicator ON fact_observations(indicator_id);

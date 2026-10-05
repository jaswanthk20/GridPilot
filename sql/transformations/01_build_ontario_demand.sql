COPY (
    SELECT
        Date,
        Hour,
        "Market Demand",
        "Ontario Demand",
        Date + Hour * INTERVAL '1 hour' AS hour_ending_timestamp
    FROM 'data/raw/PUB_Demand_2026.csv'
)
TO 'data/processed/ontario_demand_2026.parquet'
(FORMAT PARQUET);

SELECT COUNT(*)
FROM 'data/processed/ontario_demand_2026.parquet';

DESCRIBE SELECT *
FROM 'data/processed/ontario_demand_2026.parquet';
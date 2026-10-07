-- Builds an updated Parquet dataset by combining existing history with newly available demand records.

COPY (
    WITH incoming AS (
        SELECT Date, Hour, "Market Demand", "Ontario Demand", Date + Hour * INTERVAL '1 hour' AS hour_ending_timestamp
        FROM read_csv('data/raw/PUB_Demand.csv', skip = 3, header = TRUE)
    )

    SELECT Date, Hour, "Market Demand", "Ontario Demand", hour_ending_timestamp
    FROM 'data/processed/ontario_demand_2026.parquet'

    UNION ALL

    SELECT Date, Hour, "Market Demand", "Ontario Demand", hour_ending_timestamp
    FROM incoming
    WHERE hour_ending_timestamp > (SELECT MAX(hour_ending_timestamp) FROM 'data/processed/ontario_demand_2026.parquet')


)
TO 'data/processed/ontario_demand_2026_updated.parquet'
(FORMAT PARQUET);
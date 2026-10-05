-- Identifies new hourly demand records that are not yet in the processed dataset.

with incoming_transformed as (
    select Date, Hour, "Market Demand", "Ontario Demand", Date + Hour * INTERVAL '1 hour' AS hour_ending_timestamp
    FROM read_csv('data/raw/PUB_Demand.csv', skip = 3, header = true)
)

select Date, Hour, "Market Demand", "Ontario Demand", hour_ending_timestamp
FROM incoming_transformed
WHERE hour_ending_timestamp > (SELECT MAX(hour_ending_timestamp) FROM 'data/processed/ontario_demand_2026.parquet');
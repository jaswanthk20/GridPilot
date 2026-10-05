COPY (
    select Date, Hour, "Market Demand", "Ontario Demand", "hour_ending_timestamp" from 'data/processed/ontario_demand_2026.parquet'

    UNION ALL

    select Date, Hour, "Market Demand", "Ontario Demand", Date + Hour * INTERVAL '1 hour' AS hour_ending_timestamp
    FROM 'data/incoming/PUB_Demand.csv'
    WHERE hour_ending_timestamp > 
        (SELECT MAX(hour_ending_timestamp) FROM 'data/processed/ontario_demand_2026.parquet')
)

TO 'data/processed/ontario_demand_2026_updated.parquet'
(FORMAT PARQUET);
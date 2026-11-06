-- What were the 10 highest individual hourly Ontario demand observations in the dataset?

SELECT Date, Hour, "Ontario Demand"
FROM 'data/processed/ontario_demand_2026.parquet'
ORDER BY "Ontario Demand" DESC
LIMIT 10;
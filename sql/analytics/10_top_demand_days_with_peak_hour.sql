-- For each of these top 10 peak-demand days, what hour did the daily maximum occur?

WITH max_daily AS (SELECT Date, MAX("Ontario Demand") AS Max_Demand
FROM 'data/processed/ontario_demand_2026.parquet'
GROUP BY Date
ORDER BY Max_Demand DESC
LIMIT 10)

SELECT tbl.Hour, md.Date, md.Max_Demand
FROM 'data/processed/ontario_demand_2026.parquet' AS tbl
JOIN max_daily AS md
ON tbl.Date = md.Date AND tbl."Ontario Demand" = md.Max_Demand
ORDER BY md.Max_Demand DESC;

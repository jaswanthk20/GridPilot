-- What were the 10 highest-demand days, using each day's single highest hourly demand?

SELECT Date, MAX("Ontario Demand") AS Max_Demand
FROM 'data/processed/ontario_demand_2026.parquet'
GROUP BY Date
ORDER BY Max_Demand DESC
LIMIT 10;

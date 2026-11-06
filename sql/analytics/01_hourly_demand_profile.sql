-- What does average Ontario electricity demand look like for each hour of the day?

SELECT Hour, ROUND(AVG("Ontario Demand"), 2) AS AvgOntarioDemand
FROM 'data/processed/ontario_demand_2026.parquet'
GROUP BY Hour
ORDER BY Hour ASC;
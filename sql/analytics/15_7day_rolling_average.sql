-- What is the 7-day rolling average of daily Ontario electricity demand?

WITH daily_avg AS (SELECT Date, ROUND(AVG("Ontario Demand"), 2) AS DailyAvgDemand
FROM 'data/processed/ontario_demand_2026.parquet'
GROUP BY Date
HAVING COUNT(*) = 24)

SELECT Date, DailyAvgDemand, ROUND(AVG(DailyAvgDemand) OVER (ORDER BY Date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS Rolling_7_Day_Avg
FROM daily_avg
ORDER BY Date;
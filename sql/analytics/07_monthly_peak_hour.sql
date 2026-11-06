-- At what hour does each month experience its highest average demand?

WITH monthly_hourly_avg AS (SELECT MONTHNAME(Date) AS month, Hour, ROUND(AVG("Ontario Demand"), 2) AS AvgOntarioDemand
FROM 'data/processed/ontario_demand_2026.parquet'
GROUP BY month, Hour
ORDER BY month, Hour),

ranked_hours AS (SELECT month, Hour, AvgOntarioDemand, 
                    ROW_NUMBER() OVER(PARTITION BY month ORDER BY AvgOntarioDemand DESC) AS rank
                    FROM monthly_hourly_avg)

SELECT month, Hour, AvgOntarioDemand
from ranked_hours
where rank = 1


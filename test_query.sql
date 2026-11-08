WITH complete_dates AS (SELECT Date
FROM 'data/processed/ontario_demand_2026.parquet'
GROUP BY Date
HAVING COUNT(*) = 24)

SELECT MAX(Date) AS latest_complete_date
FROM complete_dates;
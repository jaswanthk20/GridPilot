SELECT
    EXTRACT(MONTH FROM Date) AS month_number,
    MONTHNAME(Date) AS month,
    Hour,
    ROUND(AVG("Ontario Demand"), 2) AS AvgOntarioDemand
FROM 'data/processed/ontario_demand_2026.parquet'
GROUP BY month_number, month, Hour
ORDER BY month_number, Hour;
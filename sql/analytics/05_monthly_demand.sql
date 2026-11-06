-- How does average Ontario demand change month by month?

SELECT EXTRACT(MONTH FROM Date) AS month_number,
MONTHNAME(Date) AS month_name, ROUND(AVG("Ontario Demand")) as AvgOntarioDemand

FROM 'data/processed/ontario_demand_2026.parquet'

GROUP BY month_number, month_name
ORDER BY month_number
-- How does demand differ across Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, and Sunday?

SELECT DAYNAME(Date) AS day_name,
       EXTRACT(ISODOW FROM Date) AS day_number,
       ROUND(AVG("Ontario Demand"), 2) AS AvgOntarioDemand

FROM 'data/processed/ontario_demand_2026.parquet'

GROUP BY day_name, day_number
ORDER BY day_number;
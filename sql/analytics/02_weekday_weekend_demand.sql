-- Do weekdays and weekends have different electricity-demand patterns?

SELECT
    CASE
        WHEN EXTRACT(ISODOW FROM Date) IN (6, 7) THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    Hour,
    ROUND(AVG("Ontario Demand"), 2) AS AvgOntarioDemand

FROM 'data/processed/ontario_demand_2026.parquet'

GROUP BY day_type, Hour
ORDER BY Hour, day_type;
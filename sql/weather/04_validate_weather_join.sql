SELECT COUNT(*)
FROM 'data/processed/ontario_demand_2026.parquet' AS demand
LEFT JOIN 'data/processed/toronto_weather_2026.parquet' AS weather
ON weather.hour_start_timestamp = demand.Date + (demand.Hour - 1) * INTERVAL '1 hour'
WHERE demand.Date <= DATE '2026-11-05' AND weather.hour_start_timestamp IS NULL
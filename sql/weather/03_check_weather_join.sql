SELECT demand.Date, demand.Hour, demand."Ontario Demand", demand.Date + (demand.Hour - 1) * INTERVAL '1 hour' AS hour_start_timestamp, weather.temperature_c
FROM 'data/processed/ontario_demand_2026.parquet' AS demand
JOIN 'data/processed/toronto_weather_2026.parquet' AS weather
ON weather.hour_start_timestamp = demand.Date + (demand.Hour - 1) * INTERVAL '1 hour'

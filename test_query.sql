select COUNT(*), max(hour_start_timestamp), min(hour_start_timestamp) 
FROM 'data/processed/demand_weather_2026.parquet'

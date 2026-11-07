COPY (
    SELECT time AS hour_start_timestamp, "temperature_2m (°C)" AS temperature_c
    FROM read_csv('data/raw/toronto_weather_2026.csv', skip = 3, header = true)
)

TO 'data/processed/toronto_weather_2026.parquet' 
(FORMAT PARQUET);

SELECT COUNT(*), MIN(hour_start_timestamp), MAX(hour_start_timestamp) 
FROM 'data/processed/toronto_weather_2026.parquet'
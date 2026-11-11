-- What is the temperature-demand correlation during colder conditions versus warmer conditions?

-- Warm conditions: temperature >= 15°C
SELECT CORR(temperature_c, "Ontario Demand") AS WarmCorrelation
FROM 'data/processed/demand_weather_2026.parquet'
WHERE temperature_c >= 15;
-- As temperature rises, demand tends to rise.

-- Cold / mild conditions: temperature < 15°C
SELECT CORR(temperature_c, "Ontario Demand") AS ColdCorrelation
FROM 'data/processed/demand_weather_2026.parquet'
WHERE temperature_c < 15;
-- As temperature rises, demand tends to fall.
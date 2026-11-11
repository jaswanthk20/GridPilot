-- How does average Ontario electricity demand change as temperature changes? Add the number of observations in each temperature band.

SELECT ROUND(AVG("Ontario Demand"), 2) AS AvgOntarioDemand, COUNT("Ontario Demand") AS ObservationCount, FLOOR((temperature_c/5))*5 AS Temp
FROM 'data/processed/demand_weather_2026.parquet'
GROUP BY Temp
ORDER BY Temp;
-- Which days experienced the largest swing between their lowest and highest electricity demand?

SELECT Date, MIN("Ontario Demand") AS DailyMin, MAX("Ontario Demand") AS DailyMax, (MAX("Ontario Demand") - MIN("Ontario Demand")) AS DemandRange
FROM 'data/processed/ontario_demand_2026.parquet'
WHERE Hour BETWEEN 1 AND 24 
GROUP BY Date
HAVING Hour BETWEEN 1 AND 24
ORDER BY DemandRange DESC

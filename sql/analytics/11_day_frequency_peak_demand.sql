-- Which hour of the day most frequently becomes the daily peak-demand hour?

WITH max_daily AS (SELECT Date, MAX("Ontario Demand") AS Max_Demand
FROM 'data/processed/ontario_demand_2026.parquet'
GROUP BY Date),

hour_freqency AS (SELECT tbl.Hour, md.Date, md.Max_Demand
FROM 'data/processed/ontario_demand_2026.parquet' AS tbl
JOIN max_daily AS md
ON tbl.Date = md.Date AND tbl."Ontario Demand" = md.Max_Demand)

SELECT hf.Hour, COUNT(*) AS Frequency
FROM hour_freqency hf
group by hf.Hour
order by Frequency desc
-- Does the most common daily peak hour change by month?

WITH max_daily AS (SELECT Date, MAX("Ontario Demand") AS Max_Demand
FROM 'data/processed/ontario_demand_2026.parquet'
GROUP BY Date),

monthly_peak_counts AS (SELECT EXTRACT(MONTH FROM tbl.Date) AS month_number, MONTHNAME(tbl.Date) AS month, tbl.Hour, COUNT(*) AS Peak_Hour_Count
FROM max_daily AS md
JOIN 'data/processed/ontario_demand_2026.parquet' AS tbl
ON tbl.Date = md.Date AND tbl."Ontario Demand" = md.Max_Demand
GROUP BY month_number, month, tbl.Hour),

ranked_hours AS (SELECT month_number, month, Hour,  Peak_Hour_Count, ROW_NUMBER() OVER (PARTITION BY month_number ORDER BY Peak_Hour_Count DESC) AS rank
FROM monthly_peak_counts)

SELECT month, Hour AS Most_Common_Peak_Hour, Peak_Hour_Count
FROM ranked_hours
WHERE rank = 1
ORDER BY month_number;
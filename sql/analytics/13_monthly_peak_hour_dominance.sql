-- What percentage of days in each month peaked at that month's most common peak hour?

WITH max_peak_daily AS (SELECT Date, MAX("Ontario Demand") AS Max_Demand
FROM 'data/processed/ontario_demand_2026.parquet'
GROUP BY Date),

peak_hours AS (SELECT mpd.Date, EXTRACT(MONTH FROM mpd.Date) AS month_number, MONTHNAME(mpd.Date) AS month, tbl.Hour
FROM 'data/processed/ontario_demand_2026.parquet' AS tbl
JOIN max_peak_daily AS mpd
ON tbl.Date = mpd.Date AND tbl."Ontario Demand" = mpd.Max_Demand),

peak_hour_counts AS (SELECT month_number, month, Hour, COUNT(*) AS Peak_Days
FROM peak_hours
GROUP BY month_number, month, Hour),

monthly_total_days AS (SELECT month_number, month, COUNT(DISTINCT Date) AS Total_Days
FROM peak_hours
GROUP BY month_number, month),

ranked_hours AS (SELECT month_number, month, Hour, Peak_Days, RANK() OVER (PARTITION BY month_number ORDER BY Peak_Days DESC) AS rank
FROM peak_hour_counts)

SELECT rh.month, rh.Hour AS Peak_Hour, rh.Peak_Days, mtd.Total_Days, ROUND(rh.Peak_Days * 100.0 / mtd.Total_Days, 2) AS Peak_Hour_Percentage
FROM ranked_hours AS rh
JOIN monthly_total_days AS mtd
ON rh.month_number = mtd.month_number
WHERE rh.rank = 1
ORDER BY rh.month_number;
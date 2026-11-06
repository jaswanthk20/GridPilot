-- What is the weekday/weekend gap by hour?
    -- DifferenceMW tells you the absolute gap between weekday and weekend demand.
    -- DifferencePct tells you how much higher weekday demand is relative to weekend demand

SELECT
    Hour,
    ROUND(AVG(CASE WHEN EXTRACT(ISODOW FROM Date) NOT IN (6, 7) THEN "Ontario Demand" END),2) AS WeekdayAvg,
    ROUND(AVG(CASE WHEN EXTRACT(ISODOW FROM Date) IN (6, 7) THEN "Ontario Demand" END),2) AS WeekendAvg,
    ROUND((WeekdayAvg - WeekendAvg),2) AS DifferenceMW,
    ROUND((WeekdayAvg - WeekendAvg) / WeekendAvg * 100,2) AS DifferencePct 

FROM 'data/processed/ontario_demand_2026.parquet'

GROUP BY Hour
ORDER BY Hour;

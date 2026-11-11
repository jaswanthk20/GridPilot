-- Calculate the ordinary Pearson correlation between temperature_c and "Ontario Demand" (Pearson Correlation)

-- Pearson correlation, which measures the direction and strength of a linear relationship between two numerical variables.
-- Range: -1 <= r <= 1
-- Positive correlation (r > 0): As temperature increases, Ontario electricity demand tends to increase.
-- Negative correlation (r < 0): As temperature increases, Ontario electricity demand tends to decrease.
-- No correlation (r = 0): There is no linear relationship between temperature and Ontario electricity demand.

SELECT CORR(temperature_c, "Ontario Demand") AS TemperatureDemandCorrelation
FROM 'data/processed/demand_weather_2026.parquet';
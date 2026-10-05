COPY 
(select date, hour, "Ontario Demand", (Date+Hour*interval '1 hour') as Timestamp 
from 'data/PUB_Demand_2026.csv') 

TO 'ontario_demand_2026.parquet' 
(FORMAT 'PARQUET');
select COUNT(*), MAX(hour_ending_timestamp)
FROM 'data/processed/ontario_demand_2026_updated.parquet';

select Date, Hour, COUNT(*)
from 'data/processed/ontario_demand_2026_updated.parquet'
group by Date, Hour
having COUNT(*) > 1;
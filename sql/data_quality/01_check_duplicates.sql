-- Checks for duplicate Date + Hour records in the demand dataset.

select date, hour, count(*)
from 'data/PUB_Demand_2026.csv'
group by date, hour
having count(*) > 1;
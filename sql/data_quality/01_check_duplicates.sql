select date, hour, count(*)
from 'data/PUB_Demand_2026.csv'
group by date, hour
having count(*) > 1;
-- Checks completed dates for fewer than 24 hourly records.

select Date, count(*)
from 'data/PUB_Demand_2026.csv'
where Date < (select max(Date) from 'data/PUB_Demand_2026.csv')
group by Date
having count(*) < 24;
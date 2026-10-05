-- Checks for zero or negative Ontario Demand values.

select *
from 'data/PUB_Demand_2026.csv'
where "Ontario Demand" <= 0;
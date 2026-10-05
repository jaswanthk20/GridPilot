-- Checks for Hour values outside the valid 1 to 24 range.

select date, hour
from 'data/PUB_Demand_2026.csv'
where hour not between 1 and 24;
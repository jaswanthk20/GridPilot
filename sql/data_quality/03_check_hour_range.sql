select date, hour
from 'data/PUB_Demand_2026.csv'
where hour not between 1 and 24;
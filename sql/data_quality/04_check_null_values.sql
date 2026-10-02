select * 
from 'data/PUB_Demand_2026.csv' 
where (Date IS NULL) or (Hour IS NULL) or ("Market Demand" IS NULL) or ("Ontario Demand" IS NULL)
-- Previews the raw IESO demand file while skipping the first three metadata rows.

select * 
from read_csv('data/raw/PUB_Demand.csv', skip = 3, header = true)
LIMIT 5;
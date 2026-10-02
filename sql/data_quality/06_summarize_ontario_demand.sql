select MIN("Ontario Demand"), MAX("Ontario Demand"), AVG("Ontario Demand")
from 'data/PUB_Demand_2026.csv';

SELECT Date, Hour, "Ontario Demand"
FROM 'data/PUB_Demand_2026.csv' 
where "Ontario Demand" = (SELECT MIN("Ontario Demand") FROM 'data/PUB_Demand_2026.csv' );

SELECT Date, Hour, "Ontario Demand"
FROM 'data/PUB_Demand_2026.csv' 
where "Ontario Demand" = (SELECT MAX("Ontario Demand") FROM 'data/PUB_Demand_2026.csv' );
/* Result: 2026-07-14, Hour 17, Ontario Demand 25,646 MW
The July 14 peak likely coincided with extreme heat, 
which may have increased air-conditioning and cooling demand across Ontario. 
"Weather may help explain electricity-demand peaks." */
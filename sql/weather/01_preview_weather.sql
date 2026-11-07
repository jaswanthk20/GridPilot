select * 
from read_csv("data/raw/toronto_weather_2026.csv", skip = 3, header = true)
LIMIT 5;
import duckdb
import urllib.parse
import urllib.request

def get_latest_complete_date():
    query = """
        SELECT Date
        FROM 'data/processed/ontario_demand_2026.parquet'
        GROUP BY Date
        HAVING COUNT(*) = 24
        ORDER BY Date DESC
        LIMIT 1"""

    latest_complete_date = (duckdb.sql(query).fetchone()[0]).strftime("%Y-%m-%d")
    return latest_complete_date

if __name__ == "__main__":

    params = { 
        "latitude": 43.690685,
        "longitude": -79.41174,
        "start_date": '2026-01-01',
        "end_date": get_latest_complete_date(),
        "timezone": "Etc/GMT+5",
        "hourly": "temperature_2m",
        "format": "csv",
    }

    base_url = "https://archive-api.open-meteo.com/v1/archive"
    url = base_url + "?" + urllib.parse.urlencode(params)
    destination = "data/raw/toronto_weather_2026.csv"
    urllib.request.urlretrieve(url, destination)
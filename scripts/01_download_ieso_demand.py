import urllib.request

url = "https://reports-public.ieso.ca/public/Demand/PUB_Demand.csv"
urllib.request.urlretrieve(url, "data/raw/PUB_Demand.csv")


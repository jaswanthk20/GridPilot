# Downloads the latest IESO hourly demand report
# and saves it as the raw source file.

import urllib.request


def download_ieso_demand():
    url = "https://reports-public.ieso.ca/public/Demand/PUB_Demand.csv"
    destination = "data/raw/PUB_Demand.csv"

    urllib.request.urlretrieve(url, destination)


if __name__ == "__main__":
    download_ieso_demand()
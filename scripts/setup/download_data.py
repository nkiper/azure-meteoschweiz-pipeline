# download_data.py
# download .csv files from MeteoSchweiz server

# %%
import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

PROJECT_DIR = os.getenv(r'PROJECT_DIR')
DATA_DIR = os.path.join(PROJECT_DIR,r'data/raw')
DOCS_DIR = os.path.join(PROJECT_DIR,r'docs')

def download_data(page_url, all_stations):
    response = requests.get(page_url)
    data = response.json()

    items_url = [link['href'] for link in data['links'] if link['rel'] == 'items'][0]

    all_items = []
    url = items_url  

    while url:
        response = requests.get(url)
        data = response.json()
        all_items.extend(data["features"])

        next_link = None
        for link in data["links"]:
            if link["rel"] == "next":
                next_link = link["href"]
                break
        
        url = next_link

    for item in all_items:
        if item['id'] not in all_stations:
            print(f"Warning: station {item['id']} not in metadata file")
        recent_csv_key = f"ogd-smn_{item['id']}_d_recent.csv"
        if recent_csv_key not in item['assets']:
            print(f"Skipping {item['id']}: no '{recent_csv_key}' asset")
            continue
        href = item['assets'][recent_csv_key]['href']
        file_path = os.path.join(DATA_DIR,item['id'])
        os.makedirs(file_path, exist_ok=True)
        try:
            response = requests.get(href)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error loading file for {item['id']}: {e}")
            continue
        with open(os.path.join(file_path,recent_csv_key), "wb") as f:
            f.write(response.content)
        

def main():
    metadata_file = os.path.join(DOCS_DIR,'ogd-smn_meta_stations.csv')
    metadata = pd.read_csv(metadata_file, delimiter=';',encoding='iso8859')

    all_stations = [station.lower() for station in metadata['station_abbr'].values]

    url = "https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn"

    download_data(url, all_stations)

if __name__ == "__main__":
    main()
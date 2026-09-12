# inspect data

import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_DIR = os.getenv(r'PROJECT_DIR')
DATA_DIR = os.path.join(PROJECT_DIR,r'data/raw')
DOCS_DIR = os.path.join(PROJECT_DIR,r'docs')

def check_data():
    metadata_file = os.path.join(DOCS_DIR,'ogd-smn_meta_stations.csv')
    metadata = pd.read_csv(metadata_file, delimiter=';',encoding='iso8859')

    all_stations = [station.lower() for station in metadata['station_abbr'].values]

    station = all_stations[0]
    filename = f"{station}/ogd-smn_{station}_d_recent.csv"
    data = pd.read_csv(os.path.join(DATA_DIR,filename), delimiter=';')
    all_columns = [key for key in data.keys()]
    error_count = 0
    station_check_count = 0
    for station in all_stations:
        filename = f"{station}/ogd-smn_{station}_d_recent.csv"
        data = pd.read_csv(os.path.join(DATA_DIR,filename), delimiter=';')
        for key in data.keys():
            if key not in all_columns:
                print(f"Warning: station {station} has column {key} not present in {all_stations[0]} dataset")
                error_count += 1
        for c in all_columns:
            if c not in data.keys():
                print(f"Warning: column {c} not found in station {station} data")
                error_count += 1
        station_check_count += 1
    print(f"finished checking {station_check_count} stations, {error_count} mismatches found")

def main():
    check_data()

if __name__ == "__main__":
    main()
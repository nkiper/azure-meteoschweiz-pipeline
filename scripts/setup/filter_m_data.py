# filter_m_data.py
# create copy of historical monthly data files that only contain data since
# the year 1975
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
PROJECT_DIR = os.getenv(r'PROJECT_DIR')
DATA_DIR = os.path.join(PROJECT_DIR,r'data/raw')
DOCS_DIR = os.path.join(PROJECT_DIR,r'docs')

def main():
    metadata_file = os.path.join(DOCS_DIR,'ogd-smn_meta_stations.csv')
    metadata = pd.read_csv(metadata_file, delimiter=';',encoding='iso8859')

    all_stations = [station.lower() for station in metadata['station_abbr'].values]
    for station_abbr in all_stations:
        data_path = os.path.join(DATA_DIR,station_abbr)
        filename = 'ogd-smn_' + station_abbr + '_m.csv'
        data = pd.read_csv(os.path.join(data_path,filename),delimiter=';')
        data['reference_timestamp'] = pd.to_datetime(data['reference_timestamp'], format='%d.%m.%Y %H:%M')
        data = data[data['reference_timestamp']>'1974-12-31']
        new_filename = 'ogd-smn_' + station_abbr + '_m1975.csv'
        data.to_csv(os.path.join(data_path,new_filename),sep=';')

if __name__ == "__main__":
    main()
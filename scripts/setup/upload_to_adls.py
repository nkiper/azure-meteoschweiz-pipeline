# upload_to_adls.py
# uploads .csv files to Azure Data Lake Storage

from dotenv import load_dotenv
import os
import time
import pandas as pd
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeDirectoryClient,
    FileSystemClient
)
from azure.core.exceptions import ResourceExistsError

load_dotenv()
PROJECT_DIR = os.getenv(r'PROJECT_DIR')
DATA_DIR = os.path.join(PROJECT_DIR,r'data/raw')
DOCS_DIR = os.path.join(PROJECT_DIR,r'docs')

ACCOUNT_NAME = os.getenv('AZURE_ACCOUNT_NAME')
ACCOUNT_KEY = os.getenv('AZURE_ACCESS_KEY')


def get_service_client_account_key(account_name, account_key) -> DataLakeServiceClient:
    account_url = f"https://{account_name}.dfs.core.windows.net"
    service_client = DataLakeServiceClient(account_url, credential=account_key)

    return service_client

def create_file_system(service_client: DataLakeServiceClient, file_system_name: str) -> FileSystemClient:
    file_system_client = service_client.create_file_system(file_system=file_system_name)

    return file_system_client

def create_directory(file_system_client: FileSystemClient, directory_name: str) -> DataLakeDirectoryClient:
    directory_client = file_system_client.create_directory(directory_name)

    return directory_client

def upload_file_to_directory(directory_client: DataLakeDirectoryClient, local_path: str, file_name: str):
    file_client = directory_client.get_file_client(file_name)

    with open(file=os.path.join(local_path, file_name), mode="rb") as data:
        file_client.upload_data(data, overwrite=True)

def main():
    service_client = get_service_client_account_key(ACCOUNT_NAME, ACCOUNT_KEY)
    try:
        file_system_client = create_file_system(service_client, 'data')
    except ResourceExistsError:
        file_system_client = service_client.get_file_system_client('data')
    except Exception as e:
        print(f"Error accessing file system: {e}")

    directory_client = create_directory(file_system_client, 'raw')
    

    metadata_file = os.path.join(DOCS_DIR,'ogd-smn_meta_stations.csv')
    metadata = pd.read_csv(metadata_file, delimiter=';',encoding='iso8859')

    all_stations = [station.lower() for station in metadata['station_abbr'].values]
    counter = 1
    for station_abbr in all_stations:
        print(f'============== {station_abbr} ({counter}/{len(all_stations)}) ==============')
        counter += 1
        try:
            t1 = time.time()
            data_path = os.path.join(DATA_DIR,station_abbr)
            filename = 'ogd-smn_' + station_abbr + '_d_recent.csv'
            upload_file_to_directory(directory_client, data_path, filename)
            t2 = time.time()
            print(f'Uploading data from station {station_abbr} took {t2-t1:.2f}s')
        except Exception as e:
            print(f'Error while uploading data from station {station_abbr}: {e}')
            continue

if __name__ == "__main__":
    main()
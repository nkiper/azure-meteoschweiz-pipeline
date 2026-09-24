# LEGACY: superseded by the Databricks notebook (Lesson 5+) — was used to load single-station data into [ogd-smn_d_recent] (now legacy_ogd-smn_d_recent)
# read .csv file, connect to azure, insert rows into table

from dotenv import load_dotenv
import pyodbc
import pandas as pd
import os
import time

load_dotenv()
PROJECT_DIR = os.getenv(r'PROJECT_DIR')
DATA_DIR = os.path.join(PROJECT_DIR,r'data/raw')
DOCS_DIR = os.path.join(PROJECT_DIR,r'docs')

CONNECTION_STRING = os.getenv('AZURE_SQL_CONNECTION_STRING')

def open_connection():
    connection = pyodbc.connect(CONNECTION_STRING)
    cursor = connection.cursor()
    return cursor, connection

def insert_station(station_abbr, table_name, cursor, connection):
    data_path = os.path.join(DATA_DIR,station_abbr)
    filename = 'ogd-smn_' + station_abbr + '_d_recent.csv'
    file_path = os.path.join(data_path, filename)

    try:
        df = pd.read_csv(file_path, sep=';')
        df['reference_timestamp'] = pd.to_datetime(df['reference_timestamp'], format='%d.%m.%Y %H:%M')
    except:
        print(f"Error loading data file for station {station_abbr}")
        return None

    column_names = list(df)


    SQL_string = 'MERGE INTO [' + table_name + '] AS target ' \
                + 'USING (SELECT ? AS ' + ', ? AS '.join(column_names) +') ' \
                + 'AS source ' \
                + 'ON target.station_abbr = source.station_abbr ' \
                + 'AND target.reference_timestamp = source.reference_timestamp ' \
                + 'WHEN NOT MATCHED THEN ' \
                + 'INSERT (' + ', '.join(column_names) + ') ' \
                + 'VALUES (source.' + ', source.'.join(column_names) + ');'  

    for i in range(len(df)):
        row_values = []
        for name in column_names:
            val = df[name][i]
            if pd.isna(val):
                row_values.append(None)
            else:
                # Convert numpy types to Python native types
                row_values.append(val.item() if hasattr(val, 'item') else val)
        cursor.execute(SQL_string, row_values)
        if (i + 1) % 50 == 0:
            print(f"Inserted {i + 1} rows...")
    connection.commit()
    print(f"Successfully inserted {len(df)} rows")

def close_connection(cursor, connection):
    cursor.close()
    connection.close()

def main():
    cursor, connection = open_connection()
    metadata_file = os.path.join(DOCS_DIR,'ogd-smn_meta_stations.csv')
    metadata = pd.read_csv(metadata_file, delimiter=';',encoding='iso8859')

    all_stations = [station.lower() for station in metadata['station_abbr'].values]
    counter = 1
    for station in all_stations[127:]:
        print(f'============== {station} ({counter}/{len(all_stations[127:])}) ==============')
        counter += 1
        try:
            t1 = time.time()
            insert_station(station,'ogd-smn_d_recent',cursor, connection)
            t2 = time.time()
            print(f'Uploading data from station {station} took {t2-t1:.2f}s')
        except Exception as e:
            print(f'Error while uploading data from station {station}: {e}')
            continue

    close_connection(cursor, connection)
    

if __name__ == "__main__":
    main()
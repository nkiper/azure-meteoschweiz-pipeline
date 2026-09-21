# load_dim_stations.py
# read stations metadata .csv file, connect to azure, insert rows into table

from dotenv import load_dotenv
import pyodbc
import pandas as pd
import os

load_dotenv()
PROJECT_DIR = os.getenv(r'PROJECT_DIR')
FILEDIR = os.path.join(PROJECT_DIR,r'docs')
FILENAME = 'ogd-smn_meta_stations.csv'

TABLENAME = 'dim_stations'

CONNECTION_STRING = os.getenv('AZURE_SQL_CONNECTION_STRING')

def open_connection():
    connection = pyodbc.connect(CONNECTION_STRING)
    cursor = connection.cursor()
    return cursor, connection

def close_connection(cursor, connection):
    cursor.close()
    connection.close()

def exclude(name):
    if (name[-3:] in ['_de', '_fr', '_it']) or ('lv95' in name):
        return True
    else:
        return False

# %%
def main():
    cursor, connection = open_connection()
    # %%
    table_name = TABLENAME
    filename = FILENAME
    file_path = os.path.join(FILEDIR,filename)
    try:
        df = pd.read_csv(file_path, delimiter=';' ,encoding='iso8859')
    except:
        print("Data file does not exist")
        return None

    df['station_data_since'] = pd.to_datetime(df['station_data_since'], format='%d.%m.%Y')

    column_names = list(df)
    column_names = [name for name in column_names if not exclude(name)]
    
    SQL_string = 'MERGE INTO [' + table_name + '] AS target ' \
                + 'USING (SELECT ? AS ' + ', ? AS '.join(column_names) +') ' \
                + 'AS source ' \
                + 'ON target.station_abbr = source.station_abbr ' \
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

    close_connection(cursor, connection)
    

if __name__ == "__main__":
    main()
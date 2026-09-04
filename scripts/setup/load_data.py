# load_data.py
# read .csv file, connect to azure, insert rows into table
 
from dotenv import load_dotenv
import pyodbc
import pandas as pd
import os

load_dotenv()
PROJECT_DIR = os.getenv(r'PROJECT_DIR')
DATA_DIR = os.path.join(PROJECT_DIR,r'data/raw')
TEST_FILENAME = 'ogd-smn_beh_d_recent.csv'
TESTING = True

CONNECTION_STRING = os.getenv('AZURE_SQL_CONNECTION_STRING')

def main():
    if not TESTING:
        print("Process data file located in data/raw")
        filename = input("Enter filename: ")
    else:
        filename = TEST_FILENAME
    file_path = os.path.join(DATA_DIR,filename)

    table_name = os.path.splitext(filename)[0]

    try:
        df = pd.read_csv(file_path, sep=';')
        df['reference_timestamp'] = pd.to_datetime(df['reference_timestamp'], format='%d.%m.%Y %H:%M')
    except:
        print("Data file does not exist")
        return None

    column_names = list(df)
    column_no = len(column_names)
    connection = pyodbc.connect(CONNECTION_STRING)
    cursor = connection.cursor()

    SQL_string = 'INSERT INTO [' + table_name + '] (' + ', '.join(column_names) \
                        + ') VALUES (' + ', '.join('?' * column_no) \
                        + ')'


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

    cursor.close()
    connection.close()
    

if __name__ == "__main__":
    main()
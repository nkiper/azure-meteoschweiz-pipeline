# load_dim_month.py
# connect to azure, insert month dims into table

from dotenv import load_dotenv
import pyodbc
import pandas as pd
import os


load_dotenv()
PROJECT_DIR = os.getenv(r'PROJECT_DIR')

TABLENAME = 'dim_month'

CONNECTION_STRING = os.getenv('AZURE_SQL_CONNECTION_STRING')

def open_connection():
    connection = pyodbc.connect(CONNECTION_STRING)
    cursor = connection.cursor()
    return cursor, connection

def close_connection(cursor, connection):
    cursor.close()
    connection.close()

def main():

    cursor, connection = open_connection()

    table_name = TABLENAME

    column_names = ['full_month_date', 'year', 'month', 'month_name', 'season', 'month_id' ]
    
    SQL_string = 'MERGE INTO [' + table_name + '] AS target ' \
                + 'USING (SELECT ? AS ' + ', ? AS '.join(column_names) +') ' \
                + 'AS source ' \
                + 'ON target.month_id = source.month_id ' \
                + 'WHEN NOT MATCHED THEN ' \
                + 'INSERT (' + ', '.join(column_names) + ') ' \
                + 'VALUES (source.' + ', source.'.join(column_names) + ');'  

    seasons = ['Winter', 'Spring', 'Summer', 'Fall']
    dti = pd.date_range('1975-01-01','2026-12-31',freq='MS')

    for i, dt in enumerate(dti):
        row_values = [dt, 
                      dt.year, 
                      dt.month, 
                      dt.month_name(), 
                      seasons[dt.month%12 // 3], 
                      dt.year*10**2+dt.month]
        cursor.execute(SQL_string, row_values)
        if (i + 1) % 50 == 0:
            print(f"Inserted {i + 1} rows...")
    connection.commit()
    print(f"Successfully inserted {len(dti)} rows")

    close_connection(cursor, connection)
    

if __name__ == "__main__":
    main()
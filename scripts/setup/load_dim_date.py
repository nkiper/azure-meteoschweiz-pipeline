# load_dim_date.py
# connect to azure, insert date dims into table

from dotenv import load_dotenv
import pyodbc
import pandas as pd
import os
import datetime

load_dotenv()
PROJECT_DIR = os.getenv(r'PROJECT_DIR')

TABLENAME = 'dim_date'

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

    column_names = ['full_date', 'year', 'month', 'month_name', 'season', 'date_id' ]
    
    SQL_string = 'MERGE INTO [' + table_name + '] AS target ' \
                + 'USING (SELECT ? AS ' + ', ? AS '.join(column_names) +') ' \
                + 'AS source ' \
                + 'ON target.date_id = source.date_id ' \
                + 'WHEN NOT MATCHED THEN ' \
                + 'INSERT (' + ', '.join(column_names) + ') ' \
                + 'VALUES (source.' + ', source.'.join(column_names) + ');'  

    seasons = ['Winter', 'Spring', 'Summer', 'Fall']
    dti = pd.date_range('2026-01-01',periods=365,freq='d')

    for i, dt in enumerate(dti):
        row_values = [dt, 
                      dt.year, 
                      dt.month, 
                      dt.month_name(), 
                      seasons[dt.month%12 // 3], 
                      dt.year*10**4+dt.month*10**2+dt.day]
        cursor.execute(SQL_string, row_values)
        if (i + 1) % 50 == 0:
            print(f"Inserted {i + 1} rows...")
    connection.commit()
    print(f"Successfully inserted {len(dti)} rows")

    close_connection(cursor, connection)
    

if __name__ == "__main__":
    main()
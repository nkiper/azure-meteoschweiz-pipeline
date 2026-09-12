# run_sql_script.py
# helper script to take .sql file contents, open pyodbc connection and execute .sql content
# %%
from dotenv import load_dotenv
import pyodbc
import pandas as pd
import os

load_dotenv()
PROJECT_DIR = os.getenv(r'PROJECT_DIR')
DATA_DIR = os.path.join(PROJECT_DIR,r'data/raw')
SCRIPT_DIR = os.path.join(PROJECT_DIR,r'scripts/sql')

CONNECTION_STRING = os.getenv('AZURE_SQL_CONNECTION_STRING')

SQL_FILE = os.path.join(SCRIPT_DIR,'create-tbl-ogd-smn_d_recent.sql')

def main():
    connection = pyodbc.connect(CONNECTION_STRING)
    cursor = connection.cursor()

    with open(SQL_FILE, 'r') as f:
        SQL_strings = f.read().replace('\n', ' ')

    for SQL_string in SQL_strings.split(';'):
        if SQL_string.strip():
            cursor.execute(SQL_string)

    connection.commit()
    print(f"Successfully executed command")

    cursor.close()
    connection.close()
        

if __name__ == "__main__":
    main()
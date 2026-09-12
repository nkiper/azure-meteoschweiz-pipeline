# generate_schema.py
# Script to read .csv file, extract column names, infer data types, and create CREATE TABLE statement

# %%
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()
PROJECT_DIR = os.getenv(r'PROJECT_DIR')

DATA_DIR = os.path.join(PROJECT_DIR,r'data/raw')
SCRIPT_DIR = os.path.join(PROJECT_DIR,r'scripts/sql')
FILEDIR = os.path.join(DATA_DIR,'beh')
FILENAME = 'ogd-smn_beh_d_recent.csv'

dtype_lookup = {
    'int64' : 'INT',
    'float64' : 'FLOAT',
    'str' : 'CHAR(3)',
    'datetime64[us]' : 'DATETIME',
    'object' : 'VARCHAR(255)'
}

UNMAPPED_TYPE = 'VARCHAR(255)'


def convert_dtype(pd_type):
    try:
        return dtype_lookup[pd_type]
    except:
        print('Warning: unmapped data type ' + pd_type + ', falling back to ' + UNMAPPED_TYPE)
        return UNMAPPED_TYPE

def get_createtable_entry(df, name):
    if name == 'station_abbr' or name == 'reference_timestamp':
        return name + ' ' + convert_dtype(str(df[name].dtype)) + ' NOT NULL'
    else:
        return name + ' ' + convert_dtype(str(df[name].dtype))

# %%
def main():
    filename = FILENAME
    file_path = os.path.join(FILEDIR,filename)

    table_name = os.path.splitext(filename[:8]+filename[12:])[0]
    
    script_name = 'create-tbl-'+table_name+'.sql'
    script_path = os.path.join(SCRIPT_DIR,script_name)

    try:
        df = pd.read_csv(file_path, sep=';')
    except:
        print("Data file does not exist")
        return None

    column_names = list(df)
    df['reference_timestamp'] = pd.to_datetime(df['reference_timestamp'], format='%d.%m.%Y %H:%M')

    try:
        script = open(script_path, 'x')
        script.close()
    except:
        ans = input("SQL script already exists. Overwrite? [y/n] ")
        if ans == 'y':
            open(script_path, 'w').close()
        else:
            return None

    with open(script_path, 'a') as f:
        f.write('IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = \'' + table_name + '\')\n')
        f.write('BEGIN\n')
        f.write('CREATE TABLE [' + table_name + '] (\n' )
        for name in column_names:
            f.write(get_createtable_entry(df, name) + ',\n')
        f. write('PRIMARY KEY (station_abbr, reference_timestamp)\n')
        f.write(')\n')
        f.write('END')


if __name__ == "__main__":
    main()

# generate_schema.py
# Script to read .csv file, extract column names, infer data types, and create CREATE TABLE statement

import pandas as pd
import os

DATA_DIR = r'/Users/natasha/Desktop/projects/azure-meteoschweiz-pipeline/data/raw'
SCRIPT_DIR = r'/Users/natasha/Desktop/projects/azure-meteoschweiz-pipeline/scripts/sql'
TEST_FILENAME = 'ogd-smn_beh_d_recent.csv'
TESTING = False

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

def main():
    if not TESTING:
        print("Process data file located in data/raw")
        filename = input("Enter filename: ")
    else:
        filename = TEST_FILENAME
    file_path = os.path.join(DATA_DIR,filename)

    script_name = 'create-tbl-'+os.path.splitext(filename)[0]+'.sql'
    script_path = os.path.join(SCRIPT_DIR,script_name)

    try:
        df = pd.read_csv(file_path, sep=';')
    except:
        print("Data file does not exist")
        return None

    column_names = list(df)
    df['reference_timestamp'] = pd.to_datetime(df['reference_timestamp'], format='%d.%m.%Y %H:%M')

    table_name = os.path.splitext(filename)[0]

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
        f.write('CREATE TABLE [' + table_name + '] (\n' )
        for name in column_names:
            f.write(get_createtable_entry(df, name) + ',\n')
        f. write('PRIMARY KEY (station_abbr, reference_timestamp)\n')
        f.write(');')


if __name__ == "__main__":
    main()

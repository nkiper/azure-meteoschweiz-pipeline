# generate_dim_parameter_schema.py
# Script to read parameters metadata .csv file, extract column names, infer data types, and 
# create CREATE TABLE statement for dimension table

from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()
PROJECT_DIR = os.getenv(r'PROJECT_DIR')

SCRIPT_DIR = os.path.join(PROJECT_DIR,r'scripts/sql')
FILEDIR = os.path.join(PROJECT_DIR,r'docs')
FILENAME = 'ogd-smn_meta_parameters.csv'

TABLENAME = 'dim_parameters'

dtype_lookup = {
    'int64' : 'INT',
    'float64' : 'FLOAT',
    'str' : 'VARCHAR(255)',
    'datetime64[us]' : 'DATETIME',
    'object' : 'VARCHAR(255)'
}

UNMAPPED_TYPE = 'VARCHAR(255)'

def exclude(name):
    if (name[-3:] in ['_de', '_fr', '_it']):
        return True
    else:
        return False


def convert_dtype(pd_type):
    try:
        return dtype_lookup[pd_type]
    except:
        print('Warning: unmapped data type ' + pd_type + ', falling back to ' + UNMAPPED_TYPE)
        return UNMAPPED_TYPE

def get_createtable_entry(df, name):
    if name == 'parameter_shortname':
        return name + ' ' + convert_dtype(str(df[name].dtype)) + ' UNIQUE NOT NULL'
    else:
        return name + ' ' + convert_dtype(str(df[name].dtype))

def main():

    filename = FILENAME
    file_path = os.path.join(FILEDIR,filename)

    table_name = TABLENAME

    script_name = 'create-tbl-'+table_name+'.sql'
    script_path = os.path.join(SCRIPT_DIR,script_name)

    try:
        df = pd.read_csv(file_path, delimiter=';' ,encoding='iso8859')
    except:
        print("Data file does not exist")
        return None

    column_names = list(df)

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
            if not exclude(name):
                f.write(get_createtable_entry(df, name) + ',\n')
        f.write('parameter_id INT IDENTITY(1,1) PRIMARY KEY\n')
        f.write(')\n')
        f.write('END')


if __name__ == "__main__":
    main()

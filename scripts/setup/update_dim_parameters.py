# update_dim_parameters.py
# update the dim_parameters table to include relationships between values with different granularities
# granularity of the parameter is encoded in parameter_shortname: second-to-last character can be:
# d: daily, h: hourly, m: monthly, t: 10 min, y: yearly

from dotenv import load_dotenv
import pyodbc
import pandas as pd
import os

load_dotenv()
PROJECT_DIR = os.getenv(r'PROJECT_DIR')
FILEDIR = os.path.join(PROJECT_DIR,r'docs')
FILENAME = 'ogd-smn_meta_parameters.csv'

TABLENAME = 'dim_parameters'

CONNECTION_STRING = os.getenv('AZURE_SQL_CONNECTION_STRING')

def open_connection():
    connection = pyodbc.connect(CONNECTION_STRING)
    cursor = connection.cursor()
    return cursor, connection

def close_connection(cursor, connection):
    cursor.close()
    connection.close()

def main():
    #%%
    cursor, connection = open_connection()

    table_name = TABLENAME

    table = pd.read_sql('SELECT * FROM ' + table_name + ';',connection)

    all_sn = table['parameter_shortname']

    for index, row in table.iterrows():
        sn = row['parameter_shortname']
        m_mod_sn = sn[:-2]+'m'+sn[-1]
        d_mod_sn = sn[:-2]+'d'+sn[-1]
        if m_mod_sn in list(all_sn):
            m_id = table[table['parameter_shortname'] == m_mod_sn]['parameter_id'].iloc[0]
            SQL_string = 'UPDATE ' + table_name \
                + ' SET corr_m_id = ? WHERE parameter_shortname = ?;'
            cursor.execute(SQL_string, [int(m_id), sn])
        if d_mod_sn in list(all_sn):
            d_id = table[table['parameter_shortname'] == d_mod_sn]['parameter_id'].iloc[0]
            SQL_string = 'UPDATE ' + table_name \
                + ' SET corr_d_id = ? WHERE parameter_shortname = ?;'
            cursor.execute(SQL_string, [int(d_id), sn])

    connection.commit()

    close_connection(cursor, connection)
    

if __name__ == "__main__":
    main()
#!/usr/bin/python3
# encoding: utf-8

'''
Adds cruise names for each sample based on the cruise number.
The cruise name is more easily identifiable for researchers who were not on the cruise. The cruise number is often not known by a researcher not on the cruise themselves.
'''

import pandas as pd
import psycopg2
import psycopg2.extras
import getpass
import sys

def add_new_column(cur, columnName):
    '''
    Adds a new column to the PSQL database
    
    Parameters
    ----------
    cur: psycopg2 cursor
    columnName: string
        Name of column to be added
        
    Returns
    -------
    None.
    '''
    columnNameLower = columnName.lower() # Name to all lower case

    cur.execute('''
                select column_name,data_type 
                from information_schema.columns 
                where table_name = 'aen'
                ''')
    res = cur.fetchall()
    
    if (columnNameLower, 'text') in res:
        print('Column "{columnName}" already exists, populating it now')
    else:
        print(f'Column "{columnName}" will be created new')
        cur.execute(f'''
                    ALTER TABLE aen
                    ADD COLUMN {columnName} TEXT;
                    ''')
        cur.execute('''
                    select column_name,data_type 
                    from information_schema.columns 
                    where table_name = 'aen'
                    ''')
        res = cur.fetchall()
        if (columnNameLower, 'text') in res:
            print(f'Column "{columnName}" has been added to the database')
    

def populate_cruise_names(cur, df):
    '''
    Populates the cruiseName column based on the content of the cruiseNumber column

    Parameters
    ----------
    cur : psycopg2 cursor
    df : pandas.dataframe
        Mapping between cruiseNumber and cruiseName

    Returns
    -------
    None.
    
    '''

    for idx, row in df.iterrows():
        cruiseName = row['cruiseName']
        cruiseNumber = row['cruiseNumber']

        cur.execute(f'''
                    UPDATE aen
                    SET cruiseName = {cruiseName}
                    WHERE cruiseNumber = {cruiseNumber}
                    ''')

    
def main():
    # Load pandas dataframe of cruise names and corresponding cruise numbers
    df = pd.read_csv('cruises.csv')
    # Connect to the database as the user running the script
    conn = psycopg2.connect('dbname=aen_db user=' + getpass.getuser())
    cur = conn.cursor()
    columnName = 'cruiseName'
    add_new_column(cur, columnName)
    populate_cruise_names(cur, df)
    conn.commit()
    cur.close()
    conn.close()
    
    
if __name__ == "__main__":
    sys.exit(main())


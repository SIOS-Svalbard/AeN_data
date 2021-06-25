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
        print(f'Column "{columnName}" already exists, populating it now')
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
    

def populate_cruise_names(cur, cruises):
    '''
    Populates the cruiseName column based on the content of the cruiseNumber column

    Parameters
    ----------
    cur : psycopg2 cursor
    cruises : pandas.dataframe
        Mapping between cruiseNumber and cruiseName

    Returns
    -------
    None.
    
    '''

    for idx, row in cruises.iterrows():
        cruiseName = row['cruiseName']
        cruiseNumber = row['cruiseNumber']

        cur.execute(f'''
                    UPDATE aen
                    SET cruiseName = {cruiseName}
                    WHERE cruiseNumber = {cruiseNumber}
                    ''')

def populate_unique_stations(cur, definedStations, dbStations):
    '''
    Populates the uniqueStation column based on station coordinates
    For stations with defined coordinates across multiple cruises (e.g. NLEG transect) column is only station name
    For stations where distance between points is significant, appending cruise name to end.

    Parameters
    ----------
    cur : psycopg2 cursor
    definedStations : pandas.dataframe
        Coordinates of stations defined in the project, consistent over numerous cruises.
    dbStations : pandas.dataframe
        Unique stations in database, coordinates averaged for all samples

    Returns
    -------
    None.
    
    '''
    
    prevname = '' # Created so only executes PSQL query for predefined stations once, even though they appear multiple times in table
    
    for idx, row in dbStations.iterrows():
        stationName = row['stationName']
        cruiseName = row['cruiseName']
        if stationName in list(definedStations['stationName']):
            if stationName != prevname:
                print(f'{stationName} to be added')
                cur.execute(f'''
                        UPDATE aen
                        SET uniqueStation = '{stationName}'
                        WHERE stationName = '{stationName}'
                        ''')
                prevname = stationName 
        else:
            uniqueStation = f'{stationName} ({cruiseName})'
            print(f'{uniqueStation} to be added')
            cur.execute(f'''
                    UPDATE aen
                    SET uniqueStation = '{uniqueStation}'
                    WHERE stationName = '{stationName}' AND cruiseName = '{cruiseName}'
                    ''')
            


    
def main():
    
    print('Executing script to add cruise names and unique station names')
    # Load pandas dataframe of cruise names and corresponding cruise numbers
    cruises = pd.read_csv('cruises.csv')
    
    # Load pandas dataframe of station names with defined coordinates
    definedStations = pd.read_csv('stations.csv')
    del definedStations['eventID'], definedStations['sampleType'] # Removing columns not needed
    
    # Connect to the database as the user running the script
    conn = psycopg2.connect('dbname=aen_db user=' + getpass.getuser())
    
    # Create dataframe of unique station names from the database with their average (mean) coordinates
    query = "select concat_ws('; ', stationname, cruisename) as stationcruise, round(avg(decimallatitude)::numeric,4) as avglat, round(avg(decimallongitude)::numeric,4) as avglong from aen where stationName is not NULL and cruisename is not NULL group by stationcruise order by stationcruise;"
    dbStations = pd.read_sql(query, conn)
    dbStations[['stationName','cruiseName']] = dbStations['stationcruise'].str.split('; ',expand=True)
    
    cur = conn.cursor()
    add_new_column(cur,columnName='cruiseName')
    populate_cruise_names(cur, cruises)
    add_new_column(cur,columnName='uniqueStation')
    populate_unique_stations(cur, definedStations, dbStations)
    conn.commit()
    cur.close()
    conn.close()
    
    
if __name__ == "__main__":
    sys.exit(main())
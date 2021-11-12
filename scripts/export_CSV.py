#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 08:28:53 2021

@author: lukem
"""

import pandas as pd
import psycopg2
import psycopg2.extras
import getpass
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import numpy as np

__all__ = []
__version__ = 0.1
__date__ = '2021-06-16'
__updated__ = '2021-08-06'

class MetadataCatalogue:
    
    def __init__(self, filePath):
        self.filePath = filePath
        self.filePathRaw = self.filePath.split('.')[0]+'_raw.csv'

    def export_CSV_from_psql(self):
        '''
        Exports metadata catalogue as CSV from the PSQL database
        Exporting this version so I have versions of the database both straight from the database and also those edited through this script.
        '''
        # Connect to the database as the user running the script
        conn = psycopg2.connect('dbname=aen_db user=' + getpass.getuser())
        cur = conn.cursor()
        
        # exporting CSV
        cur.execute(f"COPY aen TO '{self.filePathRaw}' DELIMITER ',' CSV HEADER;")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f'''The following file has been created, a CSV straight from PSQL without updates.
{self.filePathRaw}
              ''')
        
        
    def open_CSV(self):
        '''
        Open CSV as pandas dataframe
        '''
        self.df = pd.read_csv(self.filePathRaw)
    
    def add_cruise_names_column(self):
        '''
        Function to add a cruise name column, based on the cruise number. 
        This is more easily recognisable across the project, so is a better search term.

        Returns
        -------
        None.

        '''
        cruises = pd.read_csv('cruises.csv')
        
        self.df['cruisename'] = ''
        
        for idx, row in cruises.iterrows():
            
            cruiseName = row['cruiseName']
            cruiseNumber = row['cruiseNumber']
            
            self.df.loc[self.df['cruisenumber'] == cruiseNumber, 'cruisename'] = cruiseName
    
    def update_time_column_format(self,colname):
        '''
        Updating time columns to UTC ISO 8601 so they can be understood by Drupal for website

        Parameters
        ----------
        colname : string
            Name of column to update, which includes timestamps
            Format output from PSQL is YYYY-MM-DD hh:mm:ss+TZ where TZ is time zone (either 01 or 02 depending on time of year)

        Returns
        -------
        None.

        '''
        self.df[colname] = pd.to_datetime(self.df[colname], utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')     
         
    def add_timestamp_column(self):
        '''
        Adding a timestamp column which is a concatenation of date and time, required for searching by time in Drupal

        Returns
        -------
        None.

        '''
        self.df['event_timestamp'] = self.df['eventdate']+'T'+self.df['eventtime']+'Z'

    def add_symbol_beginning_and_end(self,colname):
        '''
        Adding a symbol at the beginning and end of each row in the column
        To be used on columns that might include ',' which creates problems for Drupal when reading the file as a CSV

        Parameters
        ----------
        colname : string
            Name of column to update, which includes timestamps

        Returns
        -------
        None.

        '''
        symbol = '$'
        self.df[colname] = symbol + self.df[colname] + symbol
    
    def replace_strings(self):
        '''
        Replace strings to be compatible for Drupal for SIOS website

        '''
        for col in self.df.columns:
            if self.df[col].dtype == object:
                self.df[col] = self.df[col].str.replace(r"'","", regex=True)
                self.df[col] = self.df[col].str.replace(r'"', '*', regex=True)
                self.df[col] = self.df[col].str.replace(r'$', '', regex=True)
        
    def write_updated_CSV(self):
        '''
        Open CSV as pandas dataframe
        '''
        self.df.to_csv(self.filePath, sep='|', index=False)
        print(f'The following file has been created, which includes updates required to feed metadata into Drupal.\n{self.filePath}')
        

    def output_stations_CSV(self):
        '''
        Outputting a CSV of all the stations with their coordinates
        '''
        
        stations = pd.read_csv('stations.csv') # Defined stations
    
        del stations['eventID'], stations['sampleType'] # Removing columns not needed
        
        otherStations = set(self.df['uniquestation'])  
        
        n = 0
        for station in otherStations:
            if station not in list(stations['stationName']) and type(station) == str: # Stations not already defined
                # Calculating average coordinates for each station
                n += 1
                samplesdf = self.df.loc[self.df['uniquestation'] == station]
                lat = samplesdf['decimallatitude'].median()
                lon = samplesdf['decimallongitude'].median()
                newRow = {'stationName': station, 'decimalLongitude': lon, 'decimalLatitude': lat}
                stations = stations.append(newRow, ignore_index=True)
            else:
                pass
        
        output_fp = self.filePath.split('.')[0] + '_stations.csv'
        
        stations.rename(columns = {'stationname': 'uniquestation'}, inplace = True)
        
        stations.to_csv(output_fp, index=False)
        print(f'The following CSV file has been created that includes the coordinates of each station: \n{output_fp}')
        
def main():
    '''Command line options.'''
    try:
        args = parse_options()
        filePath = args.output
        metadataCatalogue = MetadataCatalogue(filePath)
        metadataCatalogue.export_CSV_from_psql()
        metadataCatalogue.open_CSV()
        metadataCatalogue.add_cruise_names_column()
        metadataCatalogue.update_time_column_format('created')
        metadataCatalogue.update_time_column_format('modified')
        metadataCatalogue.add_timestamp_column()
        metadataCatalogue.add_symbol_beginning_and_end('metadata')
        metadataCatalogue.add_symbol_beginning_and_end('other')
        metadataCatalogue.add_symbol_beginning_and_end('history')
        metadataCatalogue.replace_strings()
        metadataCatalogue.write_updated_CSV()
        metadataCatalogue.output_stations_CSV()
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    
def parse_options():
    """
    Parse the command line options and return these. 
    """
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (
        program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

    Created by Luke Marsden on %s.

    Distributed on an "AS IS" basis without warranties
    or conditions of any kind, either express or implied.

    USAGE
''' % (program_shortdesc, str(__date__))

    # Setup argument parser
    parser = ArgumentParser(description=program_license,
                            formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument(
        'output', type=str, help='''The filepath to write the csv file to''')
    parser.add_argument('-V', '--version', action='version',
                        version=program_version_message)

    # Process arguments
    args = parser.parse_args()

    return args
    
if __name__ == "__main__":
    sys.exit(main())
    

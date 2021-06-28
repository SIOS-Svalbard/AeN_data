#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 19 11:12:43 2021

@author: lukem

The user provides a worksheet from an Excel file, including an eventID column.
The metadata for these eventIDs are pulled from the metadata catalogue,
and included in a new file that the user can download.

The output file can be more easily converted to darwin core archive or netcdf-cf, as it contains more of
the neccessary metadata in one place, with standardised column name, compared to the input,
which could contain no standardised column names.

"""

import pandas as pd
import sys
import numpy as np
from argparse import ArgumentParser, RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2021-05-19'
__updated__ = '2021-06-28'

class InputFile:
    
    def __init__(self, filePath, sheetName, headerRow, skipRows):
        self.filePath = filePath
        self.sheetName = sheetName
        self.headerRow = headerRow
        self.skipRows = skipRows
    
    def loadData(self):
        '''
        Loading data file

        Returns
        -------
        None.

        '''
        if self.filePath.endswith('.xlsx') or self.filePath.endswith('.xls'):
            self.headerRow -= 1
            self.data = pd.read_excel(self.filePath, sheet_name=self.sheetName, header=self.headerRow, skiprows=self.skipRows, engine= 'openpyxl', keep_default_na=False)
        # elif self.filePath.endswith('.csv') :
        #     self.data = pd.read_csv(self.filePath)
        
        self.data = self.data.replace(r'^\s*$', np.nan, regex=True)
        self.data = self.data.dropna(how='all', axis=1)
            
    def updateColumnNames(self):
        '''
        Checking that there is an eventID column. Aborting if not.
        Appending '_input_file' to all other column headers to distinguish them from similarly named columns from the metadata catalogue

        Returns
        -------
        None.

        '''
        headers = list(self.data.columns)
        headers = [header.lower() for header in headers] # column headers in lower case
        headers = [header.replace(" ","") for header in headers] # column headers without spaces
        
        
        if 'eventid' in headers:
            idx = headers.index('eventid')
            eventIDHeader = list(self.data.columns)[idx]
            self.data = self.data.rename(columns={eventIDHeader: "eventID"})
            
            for header in self.data.columns:
                if header != 'eventID':
                    self.data = self.data.rename(columns={header: header+"_input_file"})
        else:
            print('No eventID column found. Please check that the column name used is "eventID" and is not misspelt')
            sys.exit()
        
        

class OutputFile:
    
    def __init__(self, filePath):
        self.filePath = filePath

    def retrieveMetadata(self):
        '''
        Reading metadata from metadata catalogue
        Pull data based on a list of event IDs, provided in the data file
        Event IDs that do not exist in the metadata catalogue will not be retrieved.
        No additional row will be written to the dataframe in this case.
        
        Returns
        -------
        None.

        '''
        metadataCatalogue = pd.read_csv('/home/lukem/Documents/CruiseMetadata/SIOS_database_files/export_aen_2021_05_12.csv')
        eventIDs = self.inputFile.data['eventID'].to_list()
        df = metadataCatalogue.loc[metadataCatalogue['eventid'].isin(eventIDs)]
        
        # Creating new columns from the hstore key/value pairs in the 'other' column
        self.metadataDF = df.join(df['other'].str.extractall(r'\"(.+?)\"=>\"(.+?)\"')
             .reset_index()
             .pivot(index=['level_0', 'match'], columns=0, values=1)
             .groupby(level=0)
             .agg(lambda x: ''.join(x.dropna()))
             .replace('', np.nan)
             )
        
        self.metadataDF = self.metadataDF.drop(['other', 'history', 'modified', 'created', 'eventdate'], axis = 1)

        # Updating eventtime to UTC ISO 8601, ready to publish data. Event date removed in previous line.
        self.metadataDF['eventtime'] = pd.to_datetime(self.metadataDF['eventtime'], utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    def mergeDataAndMetadata(self):
        '''
        Merging dataframe from metadata catalogue with the dataframe from the input data sheet provided by the user
        Merging based on event ID
        EventIDs in the input file but not the metadata catalogue are still included in the merge, but the columns from the metadata catalogue remain blank
        Unregistered event IDs will be highlighted in red in the final file (see writeFile function).

        Returns
        -------
        None.

        '''
        requiredColumns = ["eventID",
             "parentEventID",
             "stationName",
             "eventTime",
             #"eventDate",
             "decimalLatitude",
             "decimalLongitude",
             "bottomDepthInMeters",
             "eventRemarks",
             "samplingProtocol",
             "sampleLocation",
             "pi_name",
             "pi_email",
             "pi_institution",
             "recordedBy",
             "sampleType"]
        
        requiredColumnsLower = [col.lower() for col in requiredColumns]
        
        self.outputDF = pd.DataFrame(columns = requiredColumns)
        
        for col in requiredColumns:
            self.outputDF[col] = self.metadataDF[col.lower()]
            
        for col in self.metadataDF.columns:
            if col.lower() not in requiredColumnsLower:
                self.outputDF[col] = self.metadataDF[col]
        
        self.outputDF = pd.merge(self.outputDF, self.inputFile.data, on='eventID', how='right')
    
    def writeREADMESheet(self, writer):
        '''
        

        Parameters
        ----------
        writer : Pandas excel writer object

        Returns
        -------
        writer : Pandas excel writer object
        Updated version with README

        '''
        
        readme = pd.DataFrame({'Read Me': [
            'This file has been created by merging data from a provided input file with data extracted from the metadata catalogue',
            '',
            'Data are merged based on the event IDs',
            'Event IDs in the input file that are not registered in the metadata column are highlighted in red',
            '',
            'Column headers from the metadata catalogue are highlighted in green',
            "Column headers from the user's input file are highlighted in yellow, and 'input_file' has been appended to the header name",
            '',
            'The metadata from the sample logs are cleaned before uploading to the metadata log',
            '1. Some fields propagate from parents to children',
            '2. Typos or errors are corrected',
            '',
            'If you notice mistakes, please contact data.nleg@unis.no so they can be corrected in the metadata log.'
            ]})
        
        readme.to_excel(writer, sheet_name='README', index=False, startrow=1, startcol=1)
        
        readmesheet = writer.sheets['README']
        
        readmesheet.set_column('B:B', 200)
        
        return writer
    
    def writeFile(self):
        '''
        Write merged dataframe to an excel sheet that will be downloaded by the user

        Returns
        -------
        None.

        '''
        writer = pd.ExcelWriter(self.filePath, engine='xlsxwriter')
        
        # readme = pd.DataFrame({'Read Me': [
        #     'This file has been created by merging data from a provided input file with data extracted from the metadata catalogue',
        #     '',
        #     'Data are merged based on the event IDs',
        #     'Event IDs in the input file that are not registered in the metadata column are highlighted in red',
        #     '',
        #     'Column headers from the metadata catalogue are highlighted in green',
        #     "Column headers from the user's input file are highlighted in yellow, and 'input_file' has been appended to the header name",
        #     '',
        #     'The metadata from the sample logs are cleaned before uploading to the metadata log',
        #     '1. Some fields propagate from parents to children',
        #     '2. Typos or errors are corrected',
        #     '',
        #     'If you notice mistakes, please contact data.nleg@unis.no so they can be corrected in the metadata log.'
        #     ]})
        
        # readme.to_excel(writer, sheet_name='README', index=False, startrow=1, startcol=1)
        
        # readmesheet = writer.sheets['README']
        
        # readmesheet.set_column('B:B', 200)
        writer = self.writeREADMESheet(writer)
        
        self.outputDF.to_excel(writer, sheet_name='Data', index=False, startrow=1)
                
        workbook = writer.book
        worksheet = writer.sheets['Data']
        
        # Set font
        DEFAULT_FONT = 'Calibri'
        DEFAULT_SIZE = 10
        workbook.formats[0].set_font_name(DEFAULT_FONT)
        workbook.formats[0].set_font_size(DEFAULT_SIZE)
    
        eventID_header_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bold': True,
            'text_wrap': False,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE+2,
            'bg_color': '#b5ecf0'
        })
        
        input_header_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bold': True,
            'text_wrap': False,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE+2,
            'bg_color': '#f0f2cf'
        })
        
        metadata_catalogue_header_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bold': True,
            'text_wrap': False,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE+2,
            'bg_color': '#c7eeb8'
        })
        
        unregistered_eventid_format = workbook.add_format({
            'bold': True,
            'bg_color': '#ec7d7d'
        })
        
        n = 0
        
        for col_num, value in enumerate(self.outputDF.columns.values):
            if value in ['eventID']:
                worksheet.write(1, col_num, value, eventID_header_format)
                worksheet.write(0, col_num, 'Unregistered events in red', eventID_header_format)
            elif value in self.inputFile.data.columns:
                worksheet.write(1, col_num, value, input_header_format)
                if n == 0:
                    worksheet.write(0, col_num, 'Columns from input file', input_header_format)
                else:
                    worksheet.write(0, col_num, '', input_header_format)
                n += 1
                
            else:
                worksheet.write(1, col_num, value, metadata_catalogue_header_format)
                worksheet.write(0, col_num, '', metadata_catalogue_header_format)
        
        worksheet.write(0, 1, 'Columns extracted from metadata catalogue', metadata_catalogue_header_format)
        
        for idx, eventid in enumerate(self.outputDF['eventID']):
            if eventid not in self.metadataDF['eventid'].to_list():
                row = idx + 2
                worksheet.write(row,0,eventid,unregistered_eventid_format)
                
        
        worksheet.set_column(2,len(self.outputDF.columns),18)
        worksheet.set_column('A:B', 36)
        
        writer.save()
        
    #def writeMetadataSheet(self, writer):
        
     
def main(argv=None):
    
    try:
        args = parse_options()
        inputFilePath = args.inputfp
        inputSheetName = args.inputsn
        headerRow = int(args.header)
        skipRows = int(args.skiprows)
        outputFilePath = args.outputfp
        
        inputFile = InputFile(inputFilePath, inputSheetName, headerRow, skipRows)    
        inputFile.loadData()
        inputFile.updateColumnNames()
        
        outputFile = OutputFile(outputFilePath)
        outputFile.inputFile = inputFile
        outputFile.retrieveMetadata()
        outputFile.mergeDataAndMetadata()
        outputFile.writeFile()
    
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

    parser.add_argument("inputfp", type=str,
                        help="The input xlsx file to read from, including an eventID column with header")
    parser.add_argument("inputsn", type=str,
                        help="The sheet name that includes the data, including an eventID column with header")
    parser.add_argument("header", type=str,
                        help="Header row number in the input file")
    parser.add_argument("skiprows", type=str,
                        help="How many rows to skip after the header row before the data begins")
    parser.add_argument("outputfp", type=str,
                        help="The location to write to, including file name (include .xlsx)")
    parser.add_argument('-V', '--version', action='version',
                        version=program_version_message)

    # Process arguments
    args = parser.parse_args()

    return args

def run(inputFilePath,inputSheetName,headerRow,skipRows,outputFilePath):
    '''
    Import and use this function to run in another script
    Main is for parsing when running in command line.

    Parameters
    ----------
    inputFilePath : String
        Filepath of xlsx including eventID column that you want to retrieve metadata for.
    inputSheetName : String
        Sheetname that includes eventID column and data that you want to retrieve metadata for.
    headerRow : Integer
        Number of row that includes headers
    skipRows : Integer
        How many rows after header row to skip before data begins (0 if data in next row)
    outputFilePath : String
        File path to write xlsx file to, with metadata retrieved from database.

    Returns
    -------
    None.

    '''
    
    inputFile = InputFile(inputFilePath, inputSheetName, headerRow, skipRows)    
    inputFile.loadData()
    inputFile.updateColumnNames()
    
    outputFile = OutputFile(outputFilePath)
    outputFile.inputFile = inputFile
    outputFile.retrieveMetadata()
    outputFile.mergeDataAndMetadata()
    outputFile.writeFile()
        
if __name__ == "__main__":
    main(sys.argv[1:])
    #sys.exit(main(sys.argv[1:]))

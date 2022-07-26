#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 14:40:28 2021

@author: lukem
"""

from retrieve_metadata_from_database import InputFile
import numpy as np
import pandas as pd
import xlsxwriter
import uuid
import darwinsheet.config.fields as fields
from datetime import datetime as dt
import os

gears = pd.read_csv('scripts/darwinsheet/config/list_gear_types.csv')
cruises = pd.read_csv('scripts/cruises.csv')

DEFAULT_FONT = 'Calibri'
DEFAULT_SIZE = 10

event_core_columns = ['eventID',
            'parentEventID',
            'samplingProtocol',
            'eventDate',
            'decimalLatitude',
            'decimalLongitude',
            'minimumDepthInMeters',
            'maximumDepthInMeters',
            'eventRemarks'
            ]

occurrence_extension_columns = ['occurrenceID',
                           'eventID',
                           'eventDate',
                           'decimalLatitude',
                           'decimalLongitude',
                           'minimumDepthInMeters',
                           'maximumDepthInMeters',
                           'scientificName',
                           'scientificNameID',
                           'recordedBy',
                           'occurrenceRemarks'
                           ]

mof_extension_columns = ['measurementID',
                         'eventID',
                         'occurrenceID',
                         'eventDate',
                         'decimalLatitude',
                         'decimalLongitude',
                         'minimumDepthInMeters',
                         'maximumDepthInMeters',
                         'measurementType',
                         'measurementTypeID',
                         'measurementValue',
                         'measurementValueID',
                         'measurementUnit',
                         'measurementUnitID'
                         ]

def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))

        return True
    except ValueError:
        return False

def find_gear_id(geartype):
    '''
    Find the persistent URI of the gear from the list_gear_types.csv file
    '''

    try:
        gear_uri = gears.loc[gears['Gear type'] == geartype, 'NVS URI'].item()
    except:
        gear_uri = ''
    if type(gear_uri) != str:
        gear_uri = ''

    return gear_uri

def removeSamplingActivities(df):

    print(df.columns)

    return df

def loadMetadataCatalogue():
    '''
    Fetching metadata from the metadata catalogue
    '''
    return pd.read_csv('/home/ubuntu/AeN_csv/export_aen_2021_11_08.csv', delimiter = '|')

def findAllParents(eventIDs, metadataCatalogue):
    '''
    Finding parents, grandparents etc of all samples.
    Continuing until sample has no parenteventid registered, therefore should be the sampling activity
    '''

    moreParents = True
    #n = 0

    parentEventIDs = []

    while moreParents == True:
        df = metadataCatalogue.loc[metadataCatalogue['eventid'].isin(eventIDs)]
        newParents = df['parenteventid'].to_list()
        newParents = [p for p in newParents if p not in eventIDs]
        [parentEventIDs.append(p) for p in newParents if type(p) == str]
        eventIDs = newParents
        if len(newParents) == 0:
            moreParents = False
        # if n == 0: # Including sampling activities included in input file
        #     inputSamplingActivities = df[df['parenteventid'].isna()]
        #     parentEventIDs = parentEventIDs + inputSamplingActivities['eventid'].tolist()
        # n = n + 1

    return list(set(parentEventIDs))

def retrieveMetadata(eventIDs, metadataCatalogue):
    # Creating new columns from the hstore key/value pairs in the 'other' column
    df = metadataCatalogue.loc[metadataCatalogue['eventid'].isin(eventIDs)]

    df = df.join(df['other'].str.extractall(r'\"(.+?)\"=>\"(.+?)\"')
         .reset_index()
         .pivot(index=['level_0', 'match'], columns=0, values=1)
         .groupby(level=0)
         .agg(lambda x: ''.join(x.dropna()))
         .replace('', np.nan)
         )

    # Updating eventdate to UTC ISO 8601, ready to publish data. Event date removed on following line.
    df['eventdate'] = df['eventdate']+'T'+df['eventtime']+'Z'

    for idx, row in df.iterrows():

        if row['geartype'] == 'CTD w/bottles':
            if type(row['parenteventid']) == str:

                df.at[idx,'samplingprotocol'] = 'Niskin bottle' + ' (' + row['samplingprotocol']+')'
            else:
                df.at[idx,'samplingprotocol'] = 'CTD with bottles' + ' (' + row['samplingprotocol']+')'
        elif type(row['geartype']) != str:
            if type(row['samplingprotocol']) == str:
                df.at[idx, 'samplingprotocol'] = row['samplingprotocol']
            else:
                df.at[idx, 'samplingprotocol'] = ''
        else:
            if type(row['samplingprotocol']) == str:
                df.at[idx,'samplingprotocol'] = row['geartype'] + ' (' + str(row['samplingprotocol'])+')'
            else:
                df.at[idx,'samplingprotocol'] = row['geartype']
        if np.isnan(row['sampledepthinmeters']) == False:
            df.at[idx,'minimumDepthInMeters'] = df.at[idx,'maximumDepthInMeters'] = row['sampledepthinmeters']

    df = df.drop(['other', 'history', 'modified', 'created', 'eventtime', 'sampledepthinmeters'], axis = 1)

    return df

class OutputFile:


    def __init__(self, filePath, eventIDs):
        self.filePath = filePath
        self.eventIDs = eventIDs
        self.metadataCatalogue = loadMetadataCatalogue()

    def make_xlsx(self):
        """
        Making an Excel file and defining which sheets to write
        """

        self.workbook = xlsxwriter.Workbook(self.filePath)

        # Set font
        self.workbook.formats[0].set_font_name(DEFAULT_FONT)
        self.workbook.formats[0].set_font_size(DEFAULT_SIZE)

        self.remove_sampling_activity_ids()

        self.create_event_core_df()

        self.create_occurrence_extension_df()

        self.create_mof_extension_df()

        self.event_core_drop_columns()

        self.write_sheet('Event Core', self.eventCoreDF)

        self.write_sheet('Occurrence Extension', self.occurrenceDF)

        self.write_sheet('MeasurementOrFacts Extension', self.mofDF)

        self.write_README()

        self.workbook.close()

    def remove_sampling_activity_ids(self):

        df = retrieveMetadata(self.eventIDs, self.metadataCatalogue)

        sampling_activities_ids = df[df['parenteventid'].isna()]['eventid'].tolist()

        for ID in sampling_activities_ids:
            self.eventIDs.remove(ID)

    def create_event_core_df(self):
        '''
        Creating a pandas dataframe for the event core

        Returns
        -------
        None.

        '''
        self.parentEventIDs = findAllParents(self.eventIDs, self.metadataCatalogue)
        self.eventCoreDF = retrieveMetadata(self.parentEventIDs, self.metadataCatalogue)

        cruisenumbers = []
        # Making cruise number the parenteventid of each sampling activity
        for idx, row in self.eventCoreDF.iterrows():
            if type(row['parenteventid']) != str:
                self.eventCoreDF['parenteventid'][idx] = row['cruisenumber']
                cruisenumbers.append(row['cruisenumber'])

        cruisenumbers = list(set(cruisenumbers))

        for cruisenumber in cruisenumbers:
            cruisedic = {
                'eventid': cruisenumber,
                'eventdate': cruises.loc[cruises['cruiseNumber'] == cruisenumber, 'eventDate'].item(),
                'samplingprotocol': 'Research cruise, ' + cruises.loc[cruises['cruiseNumber'] == cruisenumber, 'samplingProtocol'].item(),
                'eventremarks': cruises.loc[cruises['cruiseNumber'] == cruisenumber, 'cruiseName'].item()[1:-1]
                }
            self.eventCoreDF = self.eventCoreDF.append(cruisedic, ignore_index=True)

        # Ordering dataframe
        self.eventCoreDF = self.eventCoreDF.sort_values(by=['eventdate', 'parenteventid', 'minimumDepthInMeters'], ascending = [True,True,True], na_position='first')


    def event_core_drop_columns(self):
        '''
        Deleting empty columns from the event core dataframe

        Returns
        -------
        None.

        '''
        outputdf = pd.DataFrame(columns = event_core_columns)

        for col in event_core_columns:
            # termonly = col.split(':')[1]
            try:
                outputdf[col] = self.eventCoreDF[col.lower()]
            except:
                outputdf[col] = self.eventCoreDF[col]


        # Deleting empty columns from metadata catalogue
        outputdf.dropna(how='all', axis=1, inplace=True)

        self.eventCoreDF = outputdf

    def create_mof_extension_df(self):
        '''
        Create a measurementorfact extension and linking sampling activities to a controlled vocabulary where possible

        Returns
        -------
        None.

        '''

        # 0. Initialising dataframe

        self.mofDF = pd.DataFrame(columns = mof_extension_columns)

        # 1. Adding gears

        samplingGearNameCatalogue = 'http://vocab.nerc.ac.uk/collection/Q01/current/Q0100002/'
        measurementType = 'Sampling gear name'

        for idx, row in self.eventCoreDF.iterrows():

            # Not including a row for the cruise sampling event
            if is_valid_uuid(row['eventid']) == False:
                pass
            else:

                if row['geartype'] == 'CTD w/bottles':
                    if type(row['parenteventid']) == str:
                        measurementValue = 'Niskin bottle'
                        measurementValueID = 'http://vocab.nerc.ac.uk/collection/L22/current/TOOL0412/'
                    else:
                        measurementValue = 'CTD with bottles'
                        measurementValueID = find_gear_id(measurementValue)
                else:
                    measurementValue = row['geartype']
                    measurementValueID = find_gear_id(measurementValue)

                dic = {'measurementID': str(uuid.uuid1()),
                       'eventID': row['eventid'],
                       'occurrenceID': '',
                       'eventDate': row['eventdate'],
                       'decimalLatitude': row['decimallatitude'],
                       'decimalLongitude': row['decimallongitude'],
                       'minimumDepthInMeters': row['minimumDepthInMeters'],
                       'maximumDepthInMeters': row['maximumDepthInMeters'],
                       'measurementType': measurementType,
                       'measurementTypeID': samplingGearNameCatalogue,
                       'measurementValue': measurementValue,
                       'measurementValueID': measurementValueID,
                       'measurementUnit': 'NA',
                       'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/XXXX/'
                           }
                self.mofDF = self.mofDF.append(dic, ignore_index=True)

        # 2. Adding other fields from sample logs

        for idx, row in self.occurrenceMetadata.iterrows():

            for field in fields.fields:
                if field['name'] in row:
                    if 'measurementType' in field.keys():
                        try:
                            measurementvalue = row[field['name'].lower()]
                        except:
                            measurementvalue = row[field['name']]
                        if type(measurementvalue) == float:
                            if np.isnan(measurementvalue) == False:
                                dic = {'measurementID': str(uuid.uuid1()),
                                       'eventID': row['parenteventid'],
                                       'occurrenceID': row['eventid'],
                                       'eventDate': row['eventdate'],
                                       'decimalLatitude': row['decimallatitude'],
                                       'decimalLongitude': row['decimallongitude'],
                                       'minimumDepthInMeters': row['minimumDepthInMeters'],
                                       'maximumDepthInMeters': row['maximumDepthInMeters'],
                                       'measurementType': field['measurementType'],
                                       'measurementTypeID': field['measurementTypeID'],
                                       'measurementValue': measurementvalue,
                                       'measurementValueID': '',
                                       'measurementUnit': field['measurementUnit'],
                                       'measurementUnitID': field['measurementUnitID']
                                           }
                            else:
                                pass # Don't include rows where measurementValue is not provided. These were empty cells in the sample log.
                        else:
                            dic = {'measurementID': str(uuid.uuid1()),
                                   'eventID': row['parenteventid'],
                                   'occurrenceID': row['eventid'],
                                   'eventDate': row['eventdate'],
                                   'decimalLatitude': row['decimallatitude'],
                                   'decimalLongitude': row['decimallongitude'],
                                   'minimumDepthInMeters': row['minimumDepthInMeters'],
                                   'maximumDepthInMeters': row['maximumDepthInMeters'],
                                   'measurementType': field['measurementType'],
                                   'measurementTypeID': field['measurementTypeID'],
                                   'measurementValue': measurementvalue,
                                   'measurementValueID': '',
                                   'measurementUnit': field['measurementUnit'],
                                   'measurementUnitID': field['measurementUnitID']
                                       }

                            self.mofDF = self.mofDF.append(dic, ignore_index=True)



    def create_occurrence_extension_df(self):
        '''
        Creating a pandas dataframe for an occurrence extension
        This includes one row per specimen or group of specimen of the same species with the number of individuals logged
        '''

        self.occurrenceDF = pd.DataFrame(columns = occurrence_extension_columns)

        self.occurrenceMetadata = retrieveMetadata(self.eventIDs, self.metadataCatalogue)

        self.subsamplesDF = pd.DataFrame(columns = mof_extension_columns)

        for idx, row in self.occurrenceMetadata.iterrows():
            if row['parenteventid'] in list(self.occurrenceMetadata['eventid']): # Subsamples. EventID should be the grandparent of these
                eventid = self.occurrenceMetadata['parenteventid'].loc[self.occurrenceMetadata['eventid'] == row['parenteventid']]

                dic = {'measurementID': row['eventid'],
                       'eventID': eventid.item(),
                       'occurrenceID': row['parenteventid'],
                       'eventDate': row['eventdate'],
                       'decimalLatitude': row['decimallatitude'],
                       'decimalLongitude': row['decimallongitude'],
                       'minimumDepthInMeters': row['minimumDepthInMeters'],
                       'maximumDepthInMeters': row['maximumDepthInMeters'],
                       'measurementType': '',
                       'measurementTypeID': '',
                       'measurementValue': '',
                       'measurementValueID': '',
                       'measurementUnit': '',
                       'measurementUnitID': ''
                       }
                self.subsamplesDF = self.subsamplesDF.append(dic, ignore_index=True)

        # Removing subsamples to leave only one 'level' of samples, directly below the sampling activities
        # These should be the occurrences, if the user has input the right data
        # Otherwise is the highest level input.
        self.occurrenceMetadata = self.occurrenceMetadata[~self.occurrenceMetadata['eventid'].isin(self.subsamplesDF['measurementID'])]

        if len(self.occurrenceMetadata) > 0:
            # Ordering dataframe
            self.occurrenceMetadata = self.occurrenceMetadata.sort_values(by=['eventdate', 'parenteventid', 'minimumDepthInMeters'], ascending = [True,True,True], na_position='first')

            self.occurrenceDF['occurrenceID'] = self.occurrenceMetadata['eventid']

            for idx, row in self.occurrenceMetadata.iterrows():
                if row['parenteventid'] in self.occurrenceMetadata['eventid']: # Subsamples. EventID should be the grandparent of these
                    self.occurrenceDF['eventID'][idx] = self.occurrenceMetadata['parenteventid'].loc[self.occurrenceMetadata['eventid'] == row['parenteventid']]
                else:
                    self.occurrenceDF['eventID'][idx] = row['parenteventid']

            self.occurrenceDF['recordedBy'] = self.occurrenceMetadata['recordedby']
            self.occurrenceDF['eventDate'] = self.occurrenceMetadata['eventdate']
            self.occurrenceDF['decimalLongitude'] = self.occurrenceMetadata['decimallongitude']
            self.occurrenceDF['decimalLatitude'] = self.occurrenceMetadata['decimallatitude']
            self.occurrenceDF['minimumDepthInMeters'] = self.occurrenceMetadata['minimumDepthInMeters']
            self.occurrenceDF['maximumDepthInMeters'] = self.occurrenceMetadata['maximumDepthInMeters']

            try:
                self.occurrenceDF['scientificName'] = self.occurrenceMetadata['scientificName']
                self.occurrenceDF['scientificNameID'] = ''
            except:
                pass

            # Adding rows where occurrence has not been registered in the metadata catalogue
            for ID in self.eventIDs:
                if ID in self.subsamplesDF['measurementID'].values:
                    pass
                elif ID not in self.occurrenceDF['occurrenceID'].values:
                    self.occurrenceDF = self.occurrenceDF.append({'occurrenceID': ID, 'occurrenceRemarks': 'Not recorded in metadata catalogue'}, ignore_index=True)
                # Adding empty rows for duplicate IDs
                duplicates = self.eventIDs.count(ID) - 1
                if duplicates > 0:
                    for d in range(duplicates):
                        self.occurrenceDF = self.occurrenceDF.append({'occurrenceID': ID, 'occurrenceRemarks': 'Duplicate occurrenceID, two samples recorded with same ID in source file'}, ignore_index=True)

    def write_sheet(self, sheetName, df):
        '''
        Writing dataframes to Excel sheets, defining the formatting
        '''

        field_format = self.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE + 1,
            'bg_color': '#B9F6F5'
            })

        date_format = self.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bold': False,
            'text_wrap': False,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'num_format': 'dd/mm/yy'
            })

        time_format = self.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bold': False,
            'text_wrap': False,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'num_format': 'hh:mm:ss'
            })

        duplicate_format = self.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bold': True,
            'text_wrap': False,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': 'orange',
            'font_color': 'black'
            })

        not_recorded_format = self.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bold': True,
            'text_wrap': False,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': 'orange',
            'font_color': 'black'
            })

        sheet = self.workbook.add_worksheet(sheetName)

        titleRow = 0  # starting row
        startRow = titleRow + 1

        for colNum, field in enumerate(df):

            df.fillna('',inplace=True)

            sheet.write(titleRow,colNum,field,field_format)
            try:
                if field in ['eventDate', 'start_date', 'end_date']:
                    sheet.write_column(startRow,colNum,list(df[field]), date_format)
                elif field in ['eventTime', 'start_time', 'end_time']:
                    sheet.write_column(startRow,colNum,list(df[field]), time_format)
                elif colNum == 0:
                    for idx, ID in enumerate(df[field]):
                        row = startRow + idx
                        if list(df[field]).count(ID) > 1:
                            sheet.write(row,colNum,ID,duplicate_format)
                        else:
                            sheet.write(row,colNum,ID)
                if field == 'occurrenceRemarks':
                    for idx, occurrenceRemark in enumerate(df[field]):
                        row = startRow + idx
                        if occurrenceRemark == 'Duplicate occurrenceID, two samples recorded with same ID in source file':
                            sheet.write(row,colNum,occurrenceRemark,duplicate_format)
                        elif occurrenceRemark == 'Not recorded in metadata catalogue':
                            sheet.write(row,colNum,occurrenceRemark,not_recorded_format)
                        else:
                            sheet.write(row,colNum,occurrenceRemark)
                else:
                    sheet.write_column(startRow,colNum,list(df[field]))
            except:
                pass

    def write_README(self):

        sheet = self.workbook.add_worksheet('README')

        README_fmt = self.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bold': False,
            'text_wrap': False,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': 'white'
            })

        readme = pd.DataFrame({'Read Me': [
            '',
            'This file has been created by retrieving metadata from the metadata catalogue based on the eventIDs provided.',
            '',
            'The metadata was retrieved at the following time:',
            dt.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            '',
            'This file can be used to create a Darwin Core Archive. Each sheet can become a core or extension within the archive',
            '',
            'Event Core:',
            'https://rs.gbif.org/core/dwc_event_2022-02-02.xml',
            'A log of the sampling activities. It also includes a row for each cruise',
            '',
            'Occurrence Extension:',
            'https://rs.gbif.org/core/dwc_occurrence_2022-02-02.xml',
            'A log of the species and specimens recorded',
            'Linked to each sampling activity by the eventID column',
            'One row = one specimen, or multiple individuals of the same species with an individualCount column',
            'The scientificName column must be filled in.',
            'IDs in the input file that are not registered in the metadata catalogue are highlighted in orange',
            'IDs in the input file that have been logged twice in the source file are highlighted in red',
            'Note that in Nansen Legacy, all samples were logged with an eventID. OccurrenceIDs were not used',
            'In Darwin Core, only sampling events have an eventID. Occurrences have an OccurrenceID.',
            'Relevant eventIDs from the metadata catalogue have been used as occurrenceIDs in the Occurrence Extension.',
            '',
            'MeasurementOrFacts Extension:',
            'https://rs.gbif.org/extension/obis/extended_measurement_or_fact.xml',
            'A log of measurements or facts related to a sampling event or occurrence',
            'Linked to the sampling event with the sampling event ID (required)',
            'Can also be linked to an occurrence using the occurrenceID column (optional)',
            'Add your measurements related to your samples here!',
            '',
            'Data have been fetched based on the event IDs in the source file',
            '',
            'Column headers from the metadata catalogue are highlighted in green',
            '',
            'The metadata from the sample logs are cleaned before uploading to the metadata log',
            '1. Some fields propagate from parents to children',
            '2. Typos or errors are corrected',
            '',
            'If you notice any mistakes, please report them to data.nleg@unis.no so they can be corrected in the metadata catalogue.',
            'data.nleg@unis.no',
            '',
            'Useful links:',
            'Nansen Legacy Metadata Catalogue:',
            'https://sios-svalbard.org/aen/tools',
            'UUID generator:',
            'https://www.uuidgenerator.net/',
            'Darwin Core Terms:',
            'https://dwc.tdwg.org/terms/',
            'Step by step guide on how to publish FAIR Nansen Legacy datasets:',
            'https://drive.google.com/file/d/1skC5oNYFyv5jkfG4lVlVOGANbstiSTIe/view?usp=sharing',
            'Video - Darwin Core Archives and how to create them:',
            'https://www.youtube.com/watch?v=1Fuq8VZW_4c',
            '',
            '',
            '',
            ''
            ]})

        readme['blank'] = ''

        for col in [0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]:
            sheet.write_column(0,col,readme['blank'],README_fmt)
        sheet.write_column(1,1,readme['Read Me'],README_fmt)

def run(inputFilePath,inputSheetName,headerRow,dataFirstRow,outputFilePath):
    '''
    Import and use this function to run in another script

    Returns
    -------
    None.

    '''

    inputFile = InputFile(inputFilePath, inputSheetName, headerRow, dataFirstRow)
    inputFile.loadData()
    inputFile.updateColumnNames()

    eventIDs = list(inputFile.data['eventID'])
    eventIDs = [x for x in eventIDs if type(x) == str] # Removing nans)

    output = OutputFile(outputFilePath, eventIDs)
    output.make_xlsx()

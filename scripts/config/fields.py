# encoding: utf-8

'''
 -- This file is for defining the possible fields.
Each field is defined as a dictionary which should contain:

    name : short name of field
    disp_name : The displayed name of the field

Optional fields are:
    
    width : the width of the cell
    dwcid : The Darwin core identifier (an url), if this is used the rest of the names should
            follow the Darwin core  
    valid : a dictionary with definitions of the validation for the cell, as 
            per keywords used in Xlsxwriter 
            
    cell_format :  a dictionary with definitions of the format for the cell, as
                   per keywords in Xlsxwriter 

These dictionaries should then be added to the list called fields


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''
import datetime as dt

__date__ = '2018-05-22'
__updated__ = '2018-06-22'


#==============================================================================
# ID fields
#==============================================================================


uuid = {'name': 'eventID',
        'disp_name': 'Sample ID',
        'width': 34,
        'dwcid': 'http://rs.tdwg.org/dwc/terms/eventID',
        'valid': {
            'validate': 'length',
            'criteria': '==',
            'value': 32,
            'input_title': 'Sample ID',
            'input_message': '''Should be a 32 characters long UUID without -.
Could be read in with a code reader.''',
            'error_title': 'Error',
            'error_message': 'Needs to be a 32 characters long UUID'
        }
        }

puuid = {'name': 'parentEventID',
         'disp_name': 'Parent sample UUID',
         'width': 34,
         'dwcid': 'http://rs.tdwg.org/dwc/terms/parentEventID',
         'valid': {
             'validate': 'length',
             'criteria': '==',
             'value': 32,
             'input_title': 'Parent sample UUID',
             'input_message': '''ID of the sample this subsample was taken from.
Should be a 32 characters long UUID without -
Could be read in with a code reader.''',
             'error_title': 'Error',
             'error_message': 'Needs to be 32 characters long'
         }
         }


cruiseID = {'name': 'cruiseID',
            'disp_name': 'Cruise ID',
            'width': 9,
            'valid': {
                'validate': 'list',
                'source': ['2018616', '2018707', '2018709', '2018710'],
                'input_title': 'Cruise ID',
                'input_message': '''This is the same for one cruise''',
                'error_title': 'Error',
                'error_message': 'Not a valid cruise id'
            }
            }

statID = {'name': 'statID',
          'disp_name': 'Station ID',
          'width': 13,
          'valid': {
              'validate': 'integer',
              'criteria': '>',
              'value': 99,
              'input_title': 'Station ID',
              'input_message': '''This ID should come from the ship.
>= 100''',
              'error_title': 'Error',
              'error_message': 'Not a valid station id'
          }
          }

stationName = {'name': 'stationName',
               'disp_name': 'Station name',
               'width': 13,
               'valid': {
                   'validate': 'any',
                   'input_title': 'Station name',
                   'input_message': 'The name of the station. NLEG..., etc'
               }
               }


#==============================================================================
# Time and date
#==============================================================================


eventDate = {'name': 'eventDate',
             'disp_name': 'Date',
             'width': 12,
             'dwcid': 'http://rs.tdwg.org/dwc/terms/eventDate',
             'valid': {
                 'validate': 'date',
                 'criteria': 'between',
                 'minimum': dt.date(2000, 1, 1),
                 'maximum': '=TODAY()',
                 'input_title': 'Event Date',
                 'input_message': '''Can be from 2000-01-01 to today.''',
                 'error_title': 'Error',
                 'error_message': 'Not a valid date [2000-01-01, today]'
             },
             'cell_format': {
                 'num_format': 'yyyy-mm-dd'
             }
             }


start_date = {**eventDate}
start_date['name'] = 'start_date'
start_date['disp_name'] = 'Start date'
start_date['valid']['input_title'] = 'Extraction start date'
start_date.pop('dwcid')

end_date = {**start_date}
end_date['name'] = 'end_date'
end_date['disp_name'] = 'End date'
end_date['valid']['input_title'] = 'Extraction end date'


eventTime = {'name': 'eventTime',
             'disp_name': 'Time (UTC)',
             'width': 13,
             'dwcid': 'http://rs.tdwg.org/dwc/terms/eventTime',
             'valid': {
                 'validate': 'time',
                 'criteria': 'between',
                 'minimum': dt.time(0, 0, 0),
                 'maximum': dt.time(23, 59, 59, 999999),
                 'input_title': 'Event Time (UTC)',
                 'input_message': '''
The time in UTC
Format is HH:MM ''',
                 'error_title': 'Error',
                 'error_message': 'Not a valid time'
             },
             'cell_format': {
                 'num_format': 'hh:mm'
             }
             }

start_time = {**eventTime}
start_time['name'] = 'start_time'
start_time['disp_name'] = 'Start time'
start_time['valid']['input_title'] = 'Extraction start time'
start_time.pop('dwcid')

end_time = {**start_time}
end_time['name'] = 'end_time'
end_time['disp_name'] = 'End time'
end_time['valid']['input_title'] = 'Extraction end time'


#==============================================================================
# Position
#==============================================================================

decimalLatitude = {'name': 'decimalLatitude',
                   'disp_name': 'Latitude',
                   'width': 10,
                   'dwcid': 'http://rs.tdwg.org/dwc/terms/decimalLatitude',
                   'valid': {
                       'validate': 'decimal',
                       'criteria': 'between',
                       'minimum': -90,
                       'maximum': 90,
                       'input_title': 'Decimal Latitude',
                       'input_message': '''Latitude in decimal degrees.
Northern hemisphere is positive.
Example: 78.1500''',
                       'error_title': 'Error',
                       'error_message': 'Not in range [-90, 90]'
                   },
                   'cell_format': {
                       'num_format': '0.0000'
                   }
                   }

decimalLongitude = {'name': 'decimalLongitude',
                    'disp_name': 'Longitude',
                    'width': 11,
                    'dwcid': 'http://rs.tdwg.org/dwc/terms/decimalLongitude',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': 'between',
                        'minimum': -180,
                        'maximum': 180,
                        'input_title': 'Decimal Longitude',
                        'input_message': '''Longitude in decimal degrees.
East of Greenwich (0) is positive.
Example: 15.0012''',
                        'error_title': 'Error',
                        'error_message': 'Not in range [-180, 180]'
                    },
                    'cell_format': {
                        'num_format': '0.0000'
                    }
                    }

#==============================================================================
# Depths
#==============================================================================

bottomDepthInMeters = {'name': 'bottomDepthInMeters',
                       'disp_name': 'Bottom Depth (m)',
                       'width': 20,
                       'valid': {
                           'validate': 'integer',
                           'criteria': '>=',
                           'value': 0,
                           'input_title': 'Bottom Depth (m)',
                           'input_message': '''The bottom depth in integer meters.
0 is the surface.''',
                           'error_title': 'Error',
                           'error_message': 'Integer >= 0'
                       }
                       }

sampleDepthInMeters = {'name': 'sampleDepthInMeters',
                       'disp_name': 'Sample Depth (m)',
                       'width': 20,
                       'valid': {
                           'validate': 'integer',
                           'criteria': '>=',
                           'value': 0,
                           'input_title': 'Sample Depth (m)',
                           'input_message': '''The sample depth in integer meters.
0 is the surface.''',
                           'error_title': 'Error',
                           'error_message': 'Integer >= 0'
                       }
                       }


maximumDepthInMeters = {'name': 'maximumDepthInMeters',
                        'disp_name': 'Maximum depth(m)',
                        'width': 19,
                        'dwcid': 'http://rs.tdwg.org/dwc/terms/maximumDepthInMeters',
                        'valid': {
                            'validate': 'integer',
                            'criteria': 'between',
                            'minimum': 0,
                            'maximum': 9999,
                            'input_title': 'Maximum depth in (m)',
                            'input_message': '''The maximum depth in integer meters.
0 m is the surface.
9999 m is the bottom.''',
                            'error_title': 'Error',
                            'error_message': 'Integer [0, 9999]'
                        }
                        }

# This needs to be follow directly after deepest depth for the function to work
minimumDepthInMeters = {'name': 'minimumDepthInMeters',
                        'disp_name': 'Minimum depth (m)',
                        'width': 22,
                        'dwcid': 'http://rs.tdwg.org/dwc/terms/minimumDepthInMeters',
                        'valid': {
                            'validate': 'integer',
                            'criteria': '<',
                            'value': '=INDIRECT(ADDRESS(ROW(),COLUMN()-1))',
                            'input_title': 'Minimum depth in (m)',
                            'input_message': '''The minimum depth in integer meters.
0 m is the surface.
Needs to be smaller than the deepest depth''',
                            'error_title': 'Error',
                            'error_message': 'Integer [0, Deepest depth]'
                        }
                        }


#==============================================================================
# String parameters
# LABEL: Strings
#==============================================================================

# Method for making a new string property
def make_string_dict(name):
    return {'name': name,
            'disp_name': name.title().replace('_', ' '),
            'valid': {
                'validate': 'any',
                'input_title': name.title().replace('_', ' '),
                'input_message': name.title().replace('_', ' ')
            }
            }


colour = make_string_dict('colour')
smell = make_string_dict('smell')
description = make_string_dict('description')

eventRemarks = {'name': 'eventRemarks',
                'disp_name': 'Event Remarks',
                'width': 40,
                'dwcid': 'http://rs.tdwg.org/dwc/terms/eventRemarks',
                'valid': {
                         'validate': 'any',
                         'input_title': 'Event Remarks',
                         'input_message': 'Comments about the Event.'
                }
                }

fieldNotes = {'name': 'fieldNotes',
              'disp_name': 'Field Notes',
              'width': 40,
              'dwcid': 'http://rs.tdwg.org/dwc/terms/fieldNotes',
              'valid': {
                  'validate': 'any',
                  'input_title': 'Field Remarks',
                  'input_message': 'Notes from the field.'
              }
              }

occurrenceRemarks = {'name': 'occurrenceRemarks',
                     'disp_name': 'Occurrence Remarks',
                     'width': 40,
                     'dwcid': 'http://rs.tdwg.org/dwc/terms/occurrenceRemarks',
                     'valid': {
                         'validate': 'any',
                         'input_title': 'Occurrence Remarks',
                         'input_message': 'Comments or notes about the Occurrence.'
                     }
                     }

# number = {'name': 'number',
#           'disp_name': 'Number',
#           'width': 10,
#           'valid': {
#               'validate': 'integer',
#               'criteria': '>=',
#               'value': 0,
#               'input_title': 'Number of occurrences',
#               'input_message': '''Integer >= 0''',
#               'error_title': 'Error',
#               'error_message': 'Integer >= 0'
#           }
#           }

individualCount = {'name': 'individualCount',
                   'disp_name': 'Individual Count',
                   'width': 20,
                   'dwcid': 'http://rs.tdwg.org/dwc/terms/individualCount',
                   'valid': {
                       'validate': 'integer',
                       'criteria': '>',
                       'value': 0,
                       'input_title': 'Abundance',
                       'input_message': '''Integer > 0''',
                       'error_title': 'Error',
                       'error_message': 'Integer > 0'
                   }
                   }

weightInGrams = {'name': 'weightInGrams',
                 'disp_name': 'Weight (g)',
                 'width': 10,
                 'dwcid': 'http://rs.tdwg.org/dwc/terms/dynamicProperties',
                 'valid': {
                     'validate': 'decimal',
                     'criteria': '>',
                     'value': 0,
                     'input_title': 'Weight in grams (g)',
                     'input_message': '''Weight in grams''',
                     'error_title': 'Error',
                     'error_message': 'Float > 0'
                 }
                 }

sample_type = {'name': 'sample_type',
               'disp_name': 'Sample type',
               'width': 17,
               'valid': {
                   'validate': 'list',
                   'source': ['Water', 'Sediment trap', 'Water,LSN'],
                   'input_title': 'Sample type',
                   'input_message': '''Choose the sample type''',
                   'error_title': 'Error',
                   'error_message': 'Not a valid sample type'
               }
               }

water_measurement = {'name': 'water_measurement',
                     'disp_name': 'Measurement type',
                     'width': 20,
                     'long_list': True,
                     'valid': {
                         'validate': 'list',
                         'source': [
                             'deltaO18',
                             'DIC (total dissolved inorganic carbon)',
                             'AT (total alkalinity)',
                             'pH',
                             'POC/PON',
                             'CDOM',
                             'Trace elements',
                             'XRF',
                             'TOC',
                             'DOC',
                             'Protists large volume',
                             'Protists small volume',
                             'mRNA /bacteria',
                             'DNA protists/bacteria',
                             'RNA protists/bacteria',
                             'Pigments',
                             'SEM coccolithophores',
                             'Protists culturing',
                             'Bacterial production',
                             'Flow cytometry',
                             'Viral concentration',
                             'Viral production and decay'
                         ],
                         'input_title': 'Measurement type',
                         'input_message': '''Choose the intended type of measurement for this sample''',
                         'error_title': 'Error',
                         'error_message': 'Not a valid measurement type'
                     }
                     }

storage_temp = {'name': 'storage_temp',
                'disp_name': 'Storage temp',
                'width': 15,
                'valid': {
                    'validate': 'list',
                    'source': [
                        '-196 ᵒC (LN)',
                        '-80 ᵒC',
                        '-20 ᵒC',
                        'Cool room',
                        'Room temp'],
                    'input_title': 'Storage temperature',
                    'input_message': '''Choose the necessary storage temperature''',
                    'error_title': 'Error',
                    'error_message': 'Not a valid storage temperature'
                }
                }

dilution_factor = {'name': 'dilution_factor',
                   'disp_name': 'Dilution factor',
                   'width': 20,
                   'valid': {
                       'validate': 'integer',
                       'criteria': '>',
                       'value': 0,
                       'input_title': 'Dilution factor',
                       'input_message': '''Positive integer''',
                       'error_title': 'Error',
                       'error_message': 'Integer > 0'
                   }
                   }

chlorophyll = {'name': 'chlorophyll',
               'disp_name': 'Chla readout value',
               'width': 20,
               'valid': {
                       'validate': 'decimal',
                       'criteria': '>',
                       'value': 0,
                       'input_title': 'Chlorophyll A readout value',
                       'input_message': '''Positive float number''',
                       'error_title': 'Error',
                       'error_message': 'Float > 0'
               }
               }

phaeo = {'name': 'phaeo',
         'disp_name': 'Phaeo read out',
         'width': 20,
         'valid': {
             'validate': 'decimal',
             'criteria': '>',
             'value': 0,
             'input_title': 'Phaeo readout value',
             'input_message': '''Positive float number''',
             'error_title': 'Error',
             'error_message': 'Float > 0'
         }
         }


filter = {'name': 'filter',
          'disp_name': 'Filter',
          'width': 15,
          'valid': {
              'validate': 'list',
              'source': ['None', 'GFF', '10 µm'],
              'input_title': 'Filter',
              'input_message': '''Choose the filter used.
If no filtering is being done choose None''',
              'error_title': 'Error',
              'error_message': 'Not a valid filter'
          }
          }

filter_vol = {'name': 'filter_vol',
              'disp_name': 'Filter volume (ml)',
              'width': 21,
              'valid': {
                  'validate': 'integer',
                  'criteria': '>',
                  'value': 0,
                  'input_title': 'Filter volume (ml)',
                  'input_message': '''Filter volume in integer millilitres''',
                  'error_title': 'Error',
                  'error_message': 'Integer > 0'
              }
              }

methanol_vol = {'name': 'methanol_vol',
                'disp_name': 'Methanol volume (ml)',
                'width': 23,
                'valid': {
                    'validate': 'integer',
                    'criteria': '>',
                    'value': 0,
                    'input_title': 'Methanol volume (ml)',
                    'input_message': '''Methanol volume in integer millilitres''',
                    'error_title': 'Error',
                    'error_message': 'Integer > 0'
                }
                }

sample_vol = {'name': 'sample_vol',
              'disp_name': 'Sample volume (ml)',
              'width': 23,
              'valid': {
                  'validate': 'integer',
                  'criteria': '>',
                  'value': 0,
                  'input_title': 'Sample volume (ml)',
                  'input_message': '''Sample volume in integer millilitres''',
                  'error_title': 'Error',
                  'error_message': 'Integer > 0'
              }
              }


subsample_vol = {'name': 'subsample_vol',
                 'disp_name': 'Subsample volume (ml)',
                 'width': 23,
                 'valid': {
                     'validate': 'integer',
                     'criteria': '>',
                     'value': 0,
                     'input_title': 'Subsample volume (ml)',
                     'input_message': '''Subsample volume in integer millilitres''',
                     'error_title': 'Error',
                     'error_message': 'Integer > 0'
                 }
                 }

subsample_number = {'name': 'subsample_number',
                    'disp_name': 'Number of subsamples',
                    'width': 24,
                    'valid': {
                        'validate': 'integer',
                        'criteria': '>',
                        'value': 0,
                        'input_title': 'Integer number of subsamples',
                        'input_message': '''Integer > 0''',
                        'error_title': 'Error',
                        'error_message': 'Integer > 0'
                    }
                    }


sample_owner = make_string_dict('sample_owner')


#==============================================================================
# For metadata fields
#==============================================================================

title = make_string_dict('title')
title['valid']['input_message'] = 'A short descriptive title of the dataset'

abstract = make_string_dict('abstract')
abstract['valid'][
    'input_message'] = 'An abstract providing context for the dataset'

pi_name = make_string_dict('pi_name')
pi_name['disp_name'] = 'Principal investigator (PI)'

pi_email = make_string_dict('pi_email')
pi_email['disp_name'] = 'PI email'

pi_institution = make_string_dict('pi_institution')
pi_institution['disp_name'] = 'PI institution'

pi_address = make_string_dict('pi_address')
pi_address['disp_name'] = 'PI address'

project_long = make_string_dict('project_long')
project_long['disp_name'] = 'Project long name'

project_short = make_string_dict('project_short')
project_short['disp_name'] = 'Project short name'


#==============================================================================
# Species names
#==============================================================================

taxon = make_string_dict('Taxon')
taxon['dwcid'] = 'http://rs.tdwg.org/dwc/terms/Taxon'

phylum = make_string_dict('phylum')
phylum['dwcid'] = 'http://rs.tdwg.org/dwc/terms/phylum'

# can't call it class as that is a python word
classify = make_string_dict('class')
classify['dwcid'] = 'http://rs.tdwg.org/dwc/terms/class'

order = make_string_dict('order')
order['dwcid'] = 'http://rs.tdwg.org/dwc/terms/order'

family = make_string_dict('family')
family['dwcid'] = 'http://rs.tdwg.org/dwc/terms/family'

scientificName = {'name': 'scientificName',
                  'disp_name': 'Scientific Name',
                  'width': 20,
                  'dwcid': 'http://rs.tdwg.org/dwc/terms/scientificName',
                  'valid': {
                      'validate': 'any',
                      'input_title': 'Scientific Name',
                      'input_message': '''The full scientific name, with authorship and date information if known. 
When forming part of an Identification, this should be the name in lowest level taxonomic rank that can be determined'''
                  },
                  'cell_format': {
                      'left': True
                  }
                  }


dataFilename = {'name': 'dataFilename',
                'disp_name': 'Data filename',
                'width': 13,
                'valid': {
                    'validate': 'any',
                    'input_title': 'Data filename',
                    'input_message': 'The name of the datafile'
                }
                }

samplingProtocol = {'name': 'samplingProtocol',
                    'disp_name': 'Sampling protocol',
                    'width': 22,
                    'valid': {
                        'validate': 'any',
                        'input_title': 'Sampling protocol',
                        'input_message': 'Could be for instance CTD, nutrients, etc.'
                    }
                    }


#     http://rs.tdwg.org/dwc/rdf/dwcterms.rdf
# List of all the available fields
fields = [uuid, puuid, cruiseID, statID,
          eventDate, start_date, end_date,
          eventTime, start_time, end_time,
          decimalLatitude, decimalLongitude,
          bottomDepthInMeters, sampleDepthInMeters,
          maximumDepthInMeters, minimumDepthInMeters,
          taxon, phylum, classify, order, family,
          scientificName, individualCount,
          stationName, dataFilename,
          sample_type, samplingProtocol,
          water_measurement, filter,
          chlorophyll, phaeo,
          dilution_factor,
          weightInGrams,
          filter_vol, methanol_vol,
          sample_vol, subsample_vol, subsample_number,
          colour, smell, description,
          occurrenceRemarks, fieldNotes, eventRemarks,
          storage_temp, sample_owner,
          title, abstract,
          pi_name, pi_email, pi_institution, pi_address,
          project_long, project_short]

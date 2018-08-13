# encoding: utf-8

'''
 -- This file is for defining the possible fields.
Each field is defined as a dictionary which should contain:

    name : short name of field
    disp_name : The displayed name of the field

Optional fields are:
    
    width : int
            the width of the cell
    
    dwcid : str
            The Darwin core identifier (an url), if this is used the rest of the names should
            follow the Darwin core  
    
    units : str
            The measurement unit of the variable, using the standard in CF
           Examples: 'm', 'm s-1', '
    
    cf_name : str
             The variable name in the CF standard

    inherit : Boolean
             Is this a variable that can be inherited by childern? 
             If it is not present its default is False
    
    valid : dict
            a dictionary with definitions of the validation for the cell, as 
            per keywords used in Xlsxwriter 
            
    cell_format :  dict
                   a dictionary with definitions of the format for the cell, as
                   per keywords in Xlsxwriter 

These dictionaries should then be added to the list called fields


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''
import datetime as dt
import sys
import copy

__date__ = '2018-05-22'
__updated__ = '2018-07-05'


#==============================================================================
# ID fields
#==============================================================================


uuid = {'name': 'eventID',
        'disp_name': 'Sample ID',
        'width': 38,
        'dwcid': 'http://rs.tdwg.org/dwc/terms/eventID',
        'valid': {
            'validate': 'length',
            'criteria': '==',
            'value': 36,
            'input_title': 'Sample ID',
            'input_message': '''Should be a 36 character long UUID including 4 '-'.
Could be read in with a code reader.''',
            'error_title': 'Error',
            'error_message': "Needs to be a 36 characters long UUID including 4 '- '"
        }
        }


puuid = {'name': 'parentEventID',
         'disp_name': 'Parent sample UUID',
         'width': 38,
         'dwcid': 'http://rs.tdwg.org/dwc/terms/parentEventID',
         'valid': {
             'validate': 'length',
             'criteria': '==',
             'value': 36,
             'input_title': 'Parent sample UUID',
             'input_message': '''ID of the sample this subsample was taken from.
Should be a 36 characters long UUID including 4 '-'
Could be read in with a code reader.''',
             'error_title': 'Error',
             'error_message': "Needs to be a 36 characters long UUID including 4 '- '"
         }
         }


cruiseNumber = {'name': 'cruiseNumber',
                'disp_name': 'Cruise number',
                'inherit': True,
                'valid': {
                    'validate': 'list',
                    'source': ['2018616','2018791', '2018707', '2018709', '2018710'],
                    'input_title': 'Cruise Number',
                    'input_message': '''This is the same for one cruise''',
                    'error_title': 'Error',
                    'error_message': 'Not a valid cruise number '
                }
                }

statID = {'name': 'statID',
          'disp_name': 'Local Station ID',
          'inherit': True,
          'width': 13,
          'valid': {
              'validate': 'any',
              'input_title': 'Local Station ID',
              'input_message': '''This ID is a running series (per gear) for each samling event and is found in the cruise logger.
'''
          }
          }


stationName = {'name': 'stationName',
               'disp_name': 'Station Name',
               'inherit': True,
               'width': 13,
               'valid': {
                   'validate': 'any',
                   'input_title': 'Station Name',
                   'input_message': '''The name of the station. NLEG..., etc
This is recorded as SS(superstation) in the cruise logger.'''
               }
               }


#==============================================================================
# Time and date
#==============================================================================


eventDate = {'name': 'eventDate',
             'disp_name': 'Date',
             'inherit': True,
             'width': 12,
             'dwcid': 'http://rs.tdwg.org/dwc/terms/eventDate',
             'valid': {
                 'validate': 'date',
                 'criteria': 'between',
                 'minimum': dt.date(2000, 1, 1),
                 'maximum': '=TODAY()+2',
                 'input_title': 'Event Date',
                 'input_message': '''Can be from 2000-01-01 to today +2 days.''',
                 'error_title': 'Error',
                 'error_message': 'Not a valid date [2000-01-01, today + 2]'
             },
             'cell_format': {
                 'num_format': 'yyyy-mm-dd'
             }
             }


start_date = copy.deepcopy(eventDate)
start_date['name'] = 'start_date'
start_date['disp_name'] = 'Start date'
start_date['inherit'] = True
start_date['valid']['input_title'] = 'Extraction start date'
start_date.pop('dwcid')

end_date = copy.deepcopy(start_date)
end_date['name'] = 'end_date'
end_date['disp_name'] = 'End date'
end_date['inherit'] = True
end_date['valid']['input_title'] = 'Extraction end date'


eventTime = {'name': 'eventTime',
             'disp_name': 'Time (UTC)',
             'inherit': True,
             'width': 13,
             'dwcid': 'http://rs.tdwg.org/dwc/terms/eventTime',
             'valid': {
                 'validate': 'time',
                 'criteria': 'between',
                 'minimum': 0,  # Time in decimal days
                 'maximum': 0.9999999,  # Time in decimal days
                 'input_title': 'Event Time (UTC)',
                 'input_message': '''
The time in UTC
Format is HH:MM 
If MM > 59, HH will be HH + 1 ''',
                 'error_title': 'Error',
                 'error_message': 'Not a valid time'
             },
             'cell_format': {
                 'num_format': 'hh:mm'
             }
             }

# start_time = copy.deepcopy(eventTime)
# start_time['name'] = 'start_time'
# start_time['disp_name'] = 'Start time'
# start_time['valid']['input_title'] = 'Extraction start time'
# start_time.pop('dwcid')
middle_time = copy.deepcopy(eventTime)
middle_time['name'] = 'middle_time'
middle_time['disp_name'] = 'Middle time'
middle_time['inherit'] = True
middle_time['valid']['input_title'] = 'Middle time'
middle_time['valid']['input_message'] = 'Middle time for event, for instance for noting the deepest point of a trawl or net haul'+ eventTime['valid']['input_message']
middle_time.pop('dwcid')

end_time = copy.deepcopy(eventTime)
end_time['name'] = 'end_time'
end_time['disp_name'] = 'End time'
end_time['inherit'] = True
end_time['valid']['input_title'] = 'End time'
end_time['valid']['input_message'] = 'End time for event, for instance for use with a trawl or net haul'+ eventTime['valid']['input_message']
end_time.pop('dwcid')


#==============================================================================
# Position
#==============================================================================

decimalLatitude = {'name': 'decimalLatitude',
                   'disp_name': 'Latitude',
                   'inherit': True,
                   'width': 10,
                   'units': 'degrees_north',
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
                    'inherit': True,
                    'width': 11,
                    'units': 'degree_east',
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

endDecimalLatitude = {'name': 'endDecimalLatitude',
                   'disp_name': 'End Latitude',
                   'inherit': True,
                   'units': 'degrees_north',
                   'valid': {
                       'validate': 'decimal',
                       'criteria': 'between',
                       'minimum': -90,
                       'maximum': 90,
                       'input_title': 'End Decimal Latitude',
                       'input_message': '''Latitude in decimal degrees.
This is for use with for instance trawls and nets.
Northern hemisphere is positive.
Example: 78.1500''',
                       'error_title': 'Error',
                       'error_message': 'Not in range [-90, 90]'
                   },
                   'cell_format': {
                       'num_format': '0.0000'
                   }
                   }

endDecimalLongitude = {'name': 'endDecimalLongitude',
                    'disp_name': 'End Longitude',
                    'inherit': True,
                    'units': 'degree_east',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': 'between',
                        'minimum': -180,
                        'maximum': 180,
                        'input_title': 'End Decimal Longitude',
                        'input_message': '''Longitude in decimal degrees.
This is for use with for instance trawls and nets.
East of Greenwich (0) is positive.
Example: 15.0012''',
                        'error_title': 'Error',
                        'error_message': 'Not in range [-180, 180]'
                    },
                    'cell_format': {
                        'num_format': '0.0000'
                    }
                    }


middleDecimalLatitude = {'name': 'middleDecimalLatitude',
                   'disp_name': 'Middle Latitude',
                   'inherit': True,
                   'units': 'degrees_north',
                   'valid': {
                       'validate': 'decimal',
                       'criteria': 'between',
                       'minimum': -90,
                       'maximum': 90,
                       'input_title': 'Middle Decimal Latitude',
                       'input_message': '''Latitude in decimal degrees.
This is for use with for instance trawls and nets and denotes the depest point.
Northern hemisphere is positive.
Example: 78.1500''',
                       'error_title': 'Error',
                       'error_message': 'Not in range [-90, 90]'
                   },
                   'cell_format': {
                       'num_format': '0.0000'
                   }
                   }

middleDecimalLongitude = {'name': 'middleDecimalLongitude',
                    'disp_name': 'Middle Longitude',
                    'inherit': True,
                    'units': 'degree_east',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': 'between',
                        'minimum': -180,
                        'maximum': 180,
                        'input_title': 'Middle Decimal Longitude',
                        'input_message': '''Longitude in decimal degrees.
This is for use with for instance trawls and nets and denotes the depest point.
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
                       'inherit': True,
                       'units': 'm',
                       'cf_name': 'sea_floor_depth_below_sea_surface',
                       'valid': {
                           'validate': 'decimal',
                           'criteria': '>=',
                           'value': 0,
                           'input_title': 'Bottom Depth (m)',
                           'input_message': '''Sea floor depth below sea surface.
Bathymetric depth at measurement site.
0 is the surface.''',
                           'error_title': 'Error',
                           'error_message': 'Float >= 0'
                       }
                       }

sampleDepthInMeters = {'name': 'sampleDepthInMeters',
                       'disp_name': 'Sample Depth (m)',
                       'inherit': True,
                       'units': 'm',
                       'valid': {
                           'validate': 'decimal',
                           'criteria': '>=',
                           'value': 0,
                           'input_title': 'Sample Depth (m)',
                           'input_message': '''The sample depth in meters.
0 is the surface.''',
                           'error_title': 'Error',
                           'error_message': 'Float >= 0'
                       }
                       }


maximumDepthInMeters = {'name': 'maximumDepthInMeters',
                        'disp_name': 'Maximum depth(m)',
                        'inherit': True,
                        'units': 'm',
                        'dwcid': 'http://rs.tdwg.org/dwc/terms/maximumDepthInMeters',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': 'between',
                            'minimum': 0,
                            'maximum': 9999,
                            'input_title': 'Maximum depth in (m)',
                            'input_message': '''The maximum depth in meters.
0 m is the surface.
9999 m is the bottom.''',
                            'error_title': 'Error',
                            'error_message': 'Float[0, 9999]'
                        }
                        }

# If using indirect this needs to be follow directly after deepest depth for the function to work
minimumDepthInMeters = {'name': 'minimumDepthInMeters',
                        'disp_name': 'Minimum depth (m)',
                        'inherit': True,
                        'width': 22,
                        'units': 'm',
                        'dwcid': 'http://rs.tdwg.org/dwc/terms/minimumDepthInMeters',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': 'between',
                            'minimum': 0,
                            'maximum': 9999,
                            #'criteria': '<',
                            #'value': '=INDIRECT(ADDRESS(ROW(),COLUMN()-1))',
                            'input_title': 'Minimum depth in (m)',
                            'input_message': '''The minimum depth in decimal meters.
0 m is the surface.
Needs to be smaller than the maximum depth''',
                            'error_title': 'Error',
                            'error_message': 'Decimal [0, 9999]'
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

recordedBy = {'name': 'recordedBy',
              'disp_name': 'Recorded By',
              'dwcid': 'http://rs.tdwg.org/dwc/terms/recordedBy',
              'valid': {
                  'validate': 'any',
                  'input_title': 'Recorded By',
                  'input_message': '''Who has recorded/analysed the data. 
Can be a concatenated list, separated by: ';'
Example: John Doe; Ola Nordmann'''
              }
              }

recordNumber = {'name': 'recordNumber',
              'disp_name': 'Record Number',
              'dwcid': 'http://rs.tdwg.org/dwc/terms/recordNumber',
              'valid': {
                  'validate': 'any',
                  'input_title': 'Recorded Number',
                  'input_message': '''This is an additional number used to identify the sample. 
This is in addition to the sample ID (event ID)'''
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
                   'units': '1',
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

storageTemp = {'name': 'storageTemp',
                'disp_name': 'Storage temp',
                'width': 15,
                'valid': {
                    'validate': 'list',
                    'source': [
                        'neg 196 C (LN)',
                        'neg 80 C',
                        'neg 20 C',
                        'Cool room',
                        'Room temp'],
                    'input_title': 'Storage temperature',
                    'input_message': '''Choose the necessary storage temperature''',
                    'error_title': 'Error',
                    'error_message': 'Not a valid storage temperature'
                }
                }

fixative = {'name': 'fixative',
              'disp_name': 'Fixative',
              'valid': {
                  'validate': 'any',
                  'input_title': 'Fixative',
                  'input_message': '''Fixative used for sample '''
              }
              }

bottleNumber = {'name': 'bottleNumber',
                   'disp_name': 'Bottle Number',
                   'valid': {
                       'validate': 'integer',
                       'criteria': '>',
                       'value': 0,
                       'input_title': 'Bottle Number',
                       'input_message': '''The bottle number 
Could be for instance the niskin bottle number.
Positive integer''',
                       'error_title': 'Error',
                       'error_message': 'Integer > 0'
                   }
                   }

sampleLocation = {'name': 'sampleLocation',
              'disp_name': 'Sample Location',
              'valid': {
                  'validate': 'any',
                  'input_title': 'Sample Location',
                  'input_message': '''The storage location on shore.
This could for instance be an institution or something more specific'''
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

filteredVolumeInMilliliters = {'name': 'filteredVolumeInMilliliters',
              'disp_name': 'Filtered volume (mL)',
              'valid': {
                  'validate': 'decimal',
                  'criteria': '>',
                  'value': 0,
                  'input_title': 'Filtered volume (mL)',
                  'input_message': '''Filtered volume in decimal millilitres''',
                  'error_title': 'Error',
                  'error_message': 'Decimal > 0'
              }
              }

methanol_vol = {'name': 'methanol_vol',
                'disp_name': 'Methanol volume (mL)',
                'units': 'mL',
                'valid': {
                    'validate': 'integer',
                    'criteria': '>',
                    'value': 0,
                    'input_title': 'Methanol volume (mL)',
                    'input_message': '''Methanol volume in integer millilitres''',
                    'error_title': 'Error',
                    'error_message': 'Integer > 0'
                }
                }

sampleVolumeInMilliliters = {'name': 'sampleVolumeInMilliliters',
              'disp_name': 'Sample volume (mL)',
              'units': 'mL',
              'valid': {
                  'validate': 'decimal',
                  'criteria': '>',
                  'value': 0,
                  'input_title': 'Sample volume (mL)',
                  'input_message': '''Sample volume in decimal millilitres''',
                  'error_title': 'Error',
                  'error_message': 'Decimal > 0'
              }
              }


subsample_vol = {'name': 'subsample_vol',
                 'disp_name': 'Subsample volume (mL)',
                 'units': 'mL',
                 'valid': {
                     'validate': 'integer',
                     'criteria': '>',
                     'value': 0,
                     'input_title': 'Subsample volume (mL)',
                     'input_message': '''Subsample volume in integer millilitres''',
                     'error_title': 'Error',
                     'error_message': 'Integer > 0'
                 }
                 }

subsample_number = {'name': 'subsample_number',
                    'disp_name': 'Number of subsamples',
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
    'input_message'] = '''An abstract providing context for the dataset.
It should briefly explain the sampling and analysis procedures used to obtain the data.
Here it is possible to refer to a published protocol'''

pi_name = make_string_dict('pi_name')
pi_name['disp_name'] = 'Principal investigator (PI)'
pi_name['inherit'] = True

pi_email = make_string_dict('pi_email')
pi_email['disp_name'] = 'PI email'
pi_email['inherit'] = True

pi_institution = make_string_dict('pi_institution')
pi_institution['disp_name'] = 'PI institution'
pi_institution['inherit'] = True

pi_address = make_string_dict('pi_address')
pi_address['disp_name'] = 'PI address'
pi_address['inherit'] = True

project_long = make_string_dict('project_long')
project_long['disp_name'] = 'Project long name'

project_short = make_string_dict('project_short')
project_short['disp_name'] = 'Project short name'


projectID = {'name': 'projectID',
             'disp_name': 'Project ID',
             'width': 40,
             'valid': {
                 'validate': 'any',
                 'input_title': 'Project ID',
                 'input_message': '''The project ID.
For the Nansen Legacy this is:
The Nansen Legacy (RCN # 276730)'''
             }
             }

#==============================================================================
# Species names
#==============================================================================

taxon = make_string_dict('Taxon')
taxon['dwcid'] = 'http://rs.tdwg.org/dwc/terms/Taxon'

phylum = make_string_dict('phylum')
phylum['dwcid'] = 'http://rs.tdwg.org/dwc/terms/phylum'

# can't call it class as that is a python word
sex = {'name': 'sex',
                'disp_name': 'Sex',
                'dwcid': 'http://rs.tdwg.org/dwc/terms/sex',
                'valid': {
                    'validate': 'list',
                    'source': ['Male', 'Female', 'Undetermined'],
                    'input_title': 'Sex',
                    'input_message': '''Male or female. Selected from a list''',
                    'error_title': 'Error',
                    'error_message': 'Not a valid sex '
                }
                }
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
                'valid': {
                    'validate': 'any',
                    'input_title': 'Data filename',
                    'input_message': 'The name of the datafile'
                }
                }

samplingProtocol = {'name': 'samplingProtocol',
                    'disp_name': 'Sampling protocol',
                    'valid': {
                        'validate': 'any',
                        'input_title': 'Sampling protocol',
                        'input_message': '''This should be a reference to the sampling protocol used.
For exampel: Nansen Legacy sampling protocols version XX section YY.'''
                    }
                    }

gearType = {'name': 'gearType',
                    'disp_name': 'Gear Type',
                    'valid': {
                        'validate': 'any',
                        'input_title': 'Gear Type',
                        'input_message': 'The type of gear used to retrive the sample'
                    }
                    }


sampleType = {'name': 'sampleType',
                    'disp_name': 'Sample Type',
                    'valid': {
                        'validate': 'any',
                        'input_title': 'Sample Type',
                        'input_message': 'The type of sample taken'
                    }
                    }

# CF names

seaWaterTemperatueInCelsius = {'name': 'seaWaterTemperatueInCelsius',
                               'disp_name': 'Sea Water Temp (C)',
                               'units': 'Celsius',
                               'cf_name': 'sea_water_temperature',
                               'valid': {
                                   'validate': 'decimal',
                                   'criteria': '>',
                                   'value': -10,
                                   'input_title': 'Sea Water Temp (C)',
                                   'input_message': '''Sea water temperature in Celsius
Float number larger than -10 degrees C''',
                                   'error_title': 'Error',
                                   'error_message': 'Float > -10 C'
                               }
                               }

seaWaterSalinity = {'name': 'seaWaterSalinity',
                    'disp_name': 'Sea Water Salinity (1e-3)',
                    'units': '1e-3',
                    'cf_name': 'sea_water_salinity',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': '>=',
                        'value': 0,
                        'input_title': 'Sea Water Salinity',
                        'input_message': '''Sea water salinity in parts per thousand
Often using the Practical Salinity Scale of 1978
Float number larger than or equal to 0
Example: 0.029''',
                        'error_title': 'Error',
                        'error_message': 'Float >= 0'
                    }
                    }

seaWaterPressure = {'name': 'seaWaterPressure',
                    'disp_name': 'Sea Water Pressure (dbar)',
                    'units': 'dbar',
                    'cf_name': 'sea_water_pressure',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': '>',
                        'value': 0,
                        'input_title': 'Sea Water Pressure (dbar)',
                        'input_message': '''Sea water pressure in decibar
Float number larger than 0''',
                        'error_title': 'Error',
                        'error_message': 'Float > 0'
                    }
                    }


seaWaterChlorophyllA = {'name': 'seaWaterChlorophyllA',
                        'disp_name': 'Sea Chl A (mg/m^3)',
                        'units': 'mg m-3',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': '>=',
                            'value': 0,
                            'input_title': 'Sea Water Chlorophyll A (mg/m^3)',
                            'input_message': '''
Sea Water Chlorophyll in milligrams per cubic meter
Positive float number (>= 0)''',
                            'error_title': 'Error',
                            'error_message': 'Float >= 0'
                        }
                        }

seaWaterPhaeopigment = {'name': 'seaWaterPhaeopigment',
                        'disp_name': 'Sea Phaeo (mg/m^3)',
                        'units': 'mg m-3',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': '>',
                            'value': 0,
                            'input_title': 'Sea Water Phaeopigment (mg/m^3)',
                            'input_message': '''
Sea Water Phaeopigment in milligrams per cubic meter
Positive float number''',
                            'error_title': 'Error',
                            'error_message': 'Float > 0'
                        }
                        }

seaIceChlorophyllA = {'name': 'seaIceChlorophyllA',
                      'disp_name': 'Ice Chl A (mg/m^3)',
                      'units': 'mg m-3',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>=',
                          'value': 0,
                          'input_title': 'Sea Ice Chlorophyll a (mg/m^3)',
                          'input_message': '''
Sea Ice Chlorophyll in milligrams per cubic meter
Positive float number (>= 0)''',
                          'error_title': 'Error',
                          'error_message': 'Float >= 0'
                      }
                      }

seaIcePhaeopigment = {'name': 'seaIcePhaeopigment',
                      'disp_name': 'Ice Phaeo (mg/m^3)',
                      'units': 'mg m-3',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>',
                          'value': 0,
                          'input_title': 'Sea Ice Phaeopigment (mg/m^3)',
                          'input_message': '''
Sea Ice Phaeopigment in milligrams per cubic meter
Positive float number''',
                          'error_title': 'Error',
                          'error_message': 'Float > 0'
                      }
                      }

sedimentChlorophyllA = {'name': 'sedimentChlorophyllA',
                        'disp_name': 'Sediment Chl A (mg/m^3)',
                        'units': 'mg m-3',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': '>=',
                            'value': 0,
                            'input_title': 'Sediment Chlorophyll a (mg/m^3)',
                            'input_message': '''
Sediment Chlorophyll in milligrams per cubic meter
Positive float number (>= 0)''',
                            'error_title': 'Error',
                            'error_message': 'Float >= 0'
                        }
                        }

sedimentPhaeopigment = {'name': 'sedimentPhaeopigment',
                        'disp_name': 'Sediment Phaeo (mg/m^3)',
                        'units': 'mg m-3',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': '>',
                            'value': 0,
                            'input_title': 'Sediment Phaeopigment (mg/m^3)',
                            'input_message': '''
Sediment Phaeopigment in milligrams per cubic meter
Positive float number''',
                            'error_title': 'Error',
                            'error_message': 'Float > 0'
                        }
                        }


seaWaterTotalDIC = {'name': 'seaWaterTotalDIC',
                    'disp_name': 'Sea DIC (umol/kg)',
                    'units': 'umol kg-1',
                    'cf_name': 'mole_concentration_of_dissolved_inorganic_carbon_in_sea_water',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': '>=',
                        'value': 0,
                        'input_title': 'Sea Water DIC (umol/kg)',
                        'input_message': '''
Sea Water Total dissolved inorganic carbon in umol per kg
Positive float number''',
                        'error_title': 'Error',
                        'error_message': 'Float >= 0'
                    }
                    }

seaIceTotalDIC = {'name': 'seaIceTotalDIC',
                  'disp_name': 'Ice DIC (umol/kg)',
                  'units': 'umol kg-1',
                  'valid': {
                      'validate': 'decimal',
                      'criteria': '>=',
                      'value': 0,
                      'input_title': 'Sea Ice DIC (umol/kg)',
                      'input_message': '''
Sea Ice Total dissolved inorganic carbon in umol per kg
Positive float number''',
                      'error_title': 'Error',
                      'error_message': 'Float >= 0'
                  }
                  }

seaWaterDeltaO18 = {'name': 'seaWaterDeltaO18',
                    'disp_name': 'Sea delta-O-18 (1e-3)',
                    'units': '1e-3',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': '>=',
                        'value': 0,
                        'input_title': 'Sea Water delta-O-18 (1e-3)',
                        'input_message': '''
Sea Water delta-O-18 in parts per thousand 
Positive float number''',
                        'error_title': 'Error',
                        'error_message': 'Float >= 0'
                    }
                    }

seaIceDeltaO18 = {'name': 'seaIceDeltaO18',
                  'disp_name': 'Ice delta-O-18 (1e-3)',
                  'units': '1e-3',
                  'valid': {
                      'validate': 'decimal',
                      'criteria': '>=',
                      'value': 0,
                      'input_title': 'Sea Ice delta-O-18 (1e-3)',
                      'input_message': '''
Sea Ice delta-O-18 in parts per thousand 
Positive float number''',
                      'error_title': 'Error',
                      'error_message': 'Float >= 0'
                  }
                  }

seaWaterPH = {'name': 'seaWaterPH',
              'disp_name': 'Sea Water pH  (total scale)',
              'units': '1',
              'cf_name': 'sea_water_ph_reported_on_total_scale',
              'valid': {
                  'validate': 'decimal',
                  'criteria': 'between',
                  'minimum': -2,
                  'maximum': 16,
                  'input_title': 'Sea Water pH  (total scale)',
                  'input_message': '''
Is the measure of acidity of seawater, defined as the negative logarithm of 
the concentration of dissolved hydrogen ions plus bisulfate ions in a sea water
medium; it can be measured or calculated; when measured the scale is defined 
according to a series of buffers prepared in artificial seawater containing 
bisulfate.
Float in range [-2, 16]''',
                  'error_title': 'Error',
                  'error_message': 'Not in range [-2, 16]'
              }
              }

seaWaterAlkalinity = {'name': 'seaWaterAlkalinity',
                      'disp_name': 'Total Alkalinity (umol/kg)',
                      'units': 'umol kg-1',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>=',
                          'value': 0,
                          'input_title': 'Sea Water Total Alkalinity (umol/kg)',
                          'input_message': '''
Sea Water Total Alkalinity in micromols per kilogram 
Positive float number''',
                          'error_title': 'Error',
                          'error_message': 'Float >= 0'
                      }
                      }

seaWaterTOC = {'name': 'seaWaterTOC',
               'disp_name': 'TOC (mg/L)',
               'units': 'mg L-1',
               'valid': {
                   'validate': 'decimal',
                   'criteria': '>=',
                   'value': 0,
                   'input_title': 'TOC (mg/L)',
                   'input_message': '''
Sea Water Total Organic Carbon in milligrams per litre 
Positive float number''',
                   'error_title': 'Error',
                   'error_message': 'Float >= 0'
               }
               }

seaWaterPON = {'name': 'seaWaterPON',
               'disp_name': 'PON (ug/L)',
               'units': 'ug L-1',
               'valid': {
                   'validate': 'decimal',
                   'criteria': '>=',
                   'value': 0,
                   'input_title': 'PON (ug/L)',
                   'input_message': '''
Sea Water Quantification of particulate organic nitrogen in micrograms per litre 
Positive float number''',
                   'error_title': 'Error',
                   'error_message': 'Float >= 0'
               }
               }


seaWaterPOC = {'name': 'seaWaterPOC',
               'disp_name': 'POC (ug/L)',
               'units': 'ug L-1',
               'valid': {
                   'validate': 'decimal',
                   'criteria': '>=',
                   'value': 0,
                   'input_title': 'POC (ug/L)',
                   'input_message': '''
Sea Water Quantification of particulate organic carbon  in micrograms per litre 
Positive float number''',
                   'error_title': 'Error',
                   'error_message': 'Float >= 0'
               }
               }


weightInGrams = {'name': 'weightInGrams',
                 'disp_name': 'Weight (g)',
                 'units': 'g',
                 #                  'dwcid': 'http://rs.tdwg.org/dwc/terms/dynamicProperties',
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
gonadWeightInGrams = {'name': 'gonadWeightInGrams',
                 'disp_name': 'Gonad Weight (g)',
                 'units': 'g',
                 #                  'dwcid': 'http://rs.tdwg.org/dwc/terms/dynamicProperties',
                 'valid': {
                     'validate': 'decimal',
                     'criteria': '>',
                     'value': 0,
                     'input_title': 'Gonad Weight in grams (g)',
                     'input_message': '''Wet weight of the gonad in in grams''',
                     'error_title': 'Error',
                     'error_message': 'Float > 0'
                 }
                 }

liverWeightInGrams = {'name': 'liverWeightInGrams',
                 'disp_name': 'Liver Weight (g)',
                 'units': 'g',
                 #                  'dwcid': 'http://rs.tdwg.org/dwc/terms/dynamicProperties',
                 'valid': {
                     'validate': 'decimal',
                     'criteria': '>',
                     'value': 0,
                     'input_title': 'Liver Weight in grams (g)',
                     'input_message': '''Wet weight of the liver in in grams''',
                     'error_title': 'Error',
                     'error_message': 'Float > 0'
                 }
                 }
somaticWeightInGrams = {'name': 'somaticWeightInGrams',
                 'disp_name': 'Somatic Weight (g)',
                 'units': 'g',
                 #                  'dwcid': 'http://rs.tdwg.org/dwc/terms/dynamicProperties',
                 'valid': {
                     'validate': 'decimal',
                     'criteria': '>',
                     'value': 0,
                     'input_title': 'Somatic Weight in grams (g)',
                     'input_message': '''Wet weight of the fish when all inner organs are removed from the fish gonad in in grams''',
                     'error_title': 'Error',
                     'error_message': 'Float > 0'
                 }
                 }

forkLengthInMeters = {'name': 'forkLengthInMeters',
                 'disp_name': 'Fork lenght (cm)',
                 'units': 'cm',
                 #                  'dwcid': 'http://rs.tdwg.org/dwc/terms/dynamicProperties',
                 'valid': {
                     'validate': 'decimal',
                     'criteria': '>',
                     'value': 0,
                     'input_title': 'Fork lenght (cm)',
                     'input_message': '''The length of a fish measured from the most anterior part of the head to the deepest point of the notch in the tail fin in cm.
Positive decimal number''',
                     'error_title': 'Error',
                     'error_message': 'Float > 0'
                 }
                 }
maturationStage = {'name': 'maturationStage',
                 'disp_name': 'Maturation Stage',
                 'units': '1',
                 'valid': {
                     'validate': 'integer',
                     'criteria': 'between',
                     'minimum': 0,
                     'maximum': 7,
                     'input_title': 'Maturation Stage',
                     'input_message': '''On the basis of shape, size, color of the gonads and other morphological featuers, at least six maturity stages can be recongnized 
Value in range [0, 7]''',
                     'error_title': 'Error',
                     'error_message': 'Int range [0, 7]'
                 }
                 }

ectoparasites = {'name': 'ectoparasites',
                 'disp_name': 'Ectoparasites',
                 'units': '1',
                 'valid': {
                     'validate': 'integer',
                     'criteria': '>=',
                     'value': 0,
                     'input_title': 'Ectoparasites',
                     'input_message': '''Number of ectoparasites visible on the fins and gills of the fish
Integer >= 0''',
                     'error_title': 'Error',
                     'error_message': 'Int range [0, 7]'
                 }
                 }

endoparasites = {'name': 'endoparasites',
                 'disp_name': 'Endoparasites',
                 'units': '1',
                 'valid': {
                     'validate': 'integer',
                     'criteria': '>=',
                     'value': 0,
                     'input_title': 'Endoparasites',
                     'input_message': '''Number of endoparasites visible in the body cavity of the fish
Integer >= 0''',
                     'error_title': 'Error',
                     'error_message': 'Int range [0, 7]'
                 }
                 }
# List of all the available fields
fields = [getattr(sys.modules[__name__], item) for item in dir() if not item.startswith(
    "__") and isinstance(getattr(sys.modules[__name__], item), dict)]
# uuid, puuid, cruiseID, statID,
#           eventDate, start_date, end_date,
#           eventTime, start_time, end_time,
#           decimalLatitude, decimalLongitude,
#           bottomDepthInMeters, sampleDepthInMeters,
#           maximumDepthInMeters, minimumDepthInMeters,
#           taxon, phylum, classify, order, family,
#           scientificName, individualCount,
#           stationName, dataFilename,
#           sample_type, samplingProtocol,
#           water_measurement, filter,
#           chlorophyllA, phaeopigment,
#           dilution_factor,
#           weightInGrams,
#           seaWaterSalinity, seaWaterTemperatueInCelsius, seaWaterPressure,
#           filter_vol, methanol_vol,
#           sample_vol, subsample_vol, subsample_number,
#           colour, smell, description,
#           occurrenceRemarks, fieldNotes, eventRemarks,
#           storage_temp, sample_owner,
#           title, abstract,
#           pi_name, pi_email, pi_institution, pi_address,
#           recordedBy,
#           project_long, project_short, projectID]

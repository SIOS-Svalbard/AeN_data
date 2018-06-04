# encoding: utf-8

'''
 -- This file is for defining the possible fields.
Each field is defined as a dictionary which should contain:

    name : short name of field
    disp_name : The displayed name of the field

Optional fields are:
    
    width : the width of the cell
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
__updated__ = '2018-06-04'


uuid = {'name': 'uuid',
        'disp_name': 'UUID',
        'width': 34,
        'valid': {
            'validate': 'length',
            'criteria': '==',
            'value': 32,
            'input_title': 'UUID',
            'input_message': '''Read this using a code reader.
Should be 32 characters long and without -''',
            'error_title': 'Error',
            'error_message': 'Needs to be 32 characters long'
        }
        }

puuid = {'name': 'puuid',
         'disp_name': 'Parent UUID',
         'width': 34,
         'valid': {
             'validate': 'length',
             'criteria': '==',
             'value': 32,
             'input_title': 'Parent UUID',
             'input_message': '''ID of the sample this subsample was taken from.
Read this using a code reader.
Should be 32 characters long and without -''',
             'error_title': 'Error',
             'error_message': 'Needs to be 32 characters long'
         }
         }

shipid = {'name': 'shipid',
          'disp_name': 'Ship ID',
          'width': 9,
          'valid': {
              'validate': 'list',
              'source': ['2018101', '2018102', '2018103'],
              'input_title': 'Ship ID',
              'input_message': '''This is the same for one cruise''',
              'error_title': 'Error',
              'error_message': 'Not a valid ship id'
          }
          }

statid = {'name': 'statid',
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


date = {'name': 'date',
        'disp_name': 'Date',
        'width': 12,
        'valid': {
            'validate': 'date',
            'criteria': 'between',
            'minimum': dt.date(2010, 1, 1),
            'maximum': '=TODAY()',
            'input_title': 'Date',
            'input_message': '''Can be from 2010-01-01 to today.''',
            'error_title': 'Error',
            'error_message': 'Not a valid date [2010-01-01, today]'
        },
        'cell_format': {
            'num_format': 'yyyy-mm-dd'
        }
        }


start_date = {**date}
start_date['name'] = 'start_date'
start_date['disp_name'] = 'Start date'
start_date['valid']['input_title'] = 'Extraction start date'

end_date = {**date}
end_date['name'] = 'end_date'
end_date['disp_name'] = 'End date'
end_date['valid']['input_title'] = 'Extraction end date'


time = {'name': 'time',
        'disp_name': 'Time (UTC)',
        'width': 13,
        'valid': {
            'validate': 'time',
            'criteria': 'between',
            'minimum': dt.time(0, 0, 0),
            'maximum': dt.time(23, 59, 59, 999999),
            'input_title': 'Time (UTC)',
            'input_message': '''The time in UTC''',
            'error_title': 'Error',
            'error_message': 'Not a valid time'
        },
        'cell_format': {
            'num_format': 'hh:mm'
        }
        }

start_time = {**time}
start_time['name'] = 'start_time'
start_time['disp_name'] = 'Start time'
start_time['valid']['input_title'] = 'Extraction start time'

end_time = {**time}
end_time['name'] = 'end_time'
end_time['disp_name'] = 'End time'
end_time['valid']['input_title'] = 'Extraction end time'


lat = {'name': 'lat',
       'disp_name': 'Latitude',
       'width': 10,
       'valid': {
           'validate': 'decimal',
           'criteria': 'between',
           'minimum': -90,
           'maximum': 90,
           'input_title': 'Latitude',
           'input_message': '''Latitude in decimal degrees.
Northern hemisphere is positive.
Example: 78.1500''',
           'error_title': 'Error',
           'error_message': 'Not in range [-90, 90]'
       },
       'cell_format': {
           'num_format' : '0.0000'
           }
       }

long = {'name': 'long',
        'disp_name': 'Longitude',
        'width': 11,
        'valid': {
            'validate': 'decimal',
            'criteria': 'between',
            'minimum': -180,
            'maximum': 180,
            'input_title': 'Longitude',
            'input_message': '''Longitude in decimal degrees.
East of Greenwich (0) is positive.
Example: 15.0012''',
            'error_title': 'Error',
            'error_message': 'Not in range [-180, 180]'
        },
       'cell_format': {
           'num_format' : '0.0000'
           }
        }

depth = {'name': 'depth',
         'disp_name': 'Depth (m)',
         'width': 12,
         'valid': {
             'validate': 'integer',
             'criteria': '>=',
             'value': 0,
             'input_title': 'Depth (m)',
             'input_message': '''The depth in integer meters.
0 is the surface.''',
             'error_title': 'Error',
             'error_message': 'Integer >= 0'
         }
         }

deepest_depth = {'name': 'deepest_depth',
                 'disp_name': 'Deepest depth (m)',
                 'width': 19,
                 'valid': {
                     'validate': 'integer',
                     'criteria': 'between',
                     'minimum': 0,
                     'maximum': 9999,
                     'input_title': 'Deepest depth in (m)',
                     'input_message': '''The deepest depth in integer meters.
0 m is the surface.
9999 m is the bottom.''',
                     'error_title': 'Error',
                     'error_message': 'Integer [0, 9999]'
                 }
                 }

# This needs to be follow directly after deepest depth for the function to work
shallowest_depth = {'name': 'shallowest_depth',
                    'disp_name': 'Shallowest depth (m)',
                    'width': 22,
                    'valid': {
                        'validate': 'integer',
                        'criteria': '<',
                        'value': '=INDIRECT(ADDRESS(ROW(),COLUMN()-1))',
                        'input_title': 'Shallowest depth in (m)',
                        'input_message': '''The shallowest depth in integer meters.
0 m is the surface.
Needs to be smaller than the deepest depth''',
                        'error_title': 'Error',
                        'error_message': 'Integer [0, Deepest depth]'
                    }
                    }


def make_string_dict(name):
    return {'name': name.lower(),
            'disp_name': name.title().replace('_',' '),
            'valid': {
        'validate': 'any',
        'input_title': name.title().replace('_',' '),
        'input_message': name.title().replace('_',' ')
    }
    }

taxon = make_string_dict('taxon')

phylum = make_string_dict('phylum')

classify = make_string_dict('classify')
order = make_string_dict('order')
family = make_string_dict('family')
species = make_string_dict('species')
species['width'] = 20
species['cell_format'] = {
    'left': True
}

colour = make_string_dict('colour')
smell = make_string_dict('smell')
description = make_string_dict('description')
comment = make_string_dict('comment')
comment['valid']['input_message'] = 'Optional: for comment'


number = {'name': 'number',
          'disp_name': 'Number',
          'width': 10,
          'valid': {
              'validate': 'integer',
              'criteria': '>=',
              'value': 0,
              'input_title': 'Number of occurrences',
              'input_message': '''Integer >= 0''',
              'error_title': 'Error',
              'error_message': 'Integer >= 0'
          }
          }

abundance = {'name': 'abundance',
             'disp_name': 'Abundance',
             'width': 13,
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

mass = {'name': 'mass',
        'disp_name': 'Mass (g)',
        'width': 10,
        'valid': {
            'validate': 'decimal',
            'criteria': '>',
            'value': 0,
            'input_title': 'Mass (g)',
            'input_message': '''Mass in grams''',
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

storage_temp  = {'name': 'storage_temp',
               'disp_name': 'Storage temp',
               'width': 15,
               'valid': {
                   'validate': 'list',
                   'source': [
                       '-196 ᵒC (LN)',
                       '-80 ᵒC',
                       '-20 ᵒC',
                       'Cool room',
                       'Room temp' ],
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
              'source': ['None','GFF', '10 µm'],
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


# For metadata fields

title = make_string_dict('title')
title['valid']['input_message'] = 'A short descriptive title of the dataset'

abstract = make_string_dict('abstract')
abstract['valid']['input_message'] ='An abstract providing context for the dataset'

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





# List of all the available fields
fields = [uuid, puuid, shipid, statid,
          date, start_date, end_date,
          time, start_time, end_time,
          lat, long,
          depth, deepest_depth, shallowest_depth,
          taxon, phylum, classify, order, family,
          species, number, abundance,
          sample_type, water_measurement, filter,
          chlorophyll, phaeo,
          dilution_factor,
          mass,
          filter_vol, methanol_vol,
          sample_vol, subsample_vol, subsample_number,
          colour, smell, description,
          comment, storage_temp, sample_owner,
          title, abstract,
          pi_name, pi_email, pi_institution, pi_address,
          project_long, project_short]

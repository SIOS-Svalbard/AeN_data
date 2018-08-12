#!/usr/bin/python3
# encoding: utf-8
'''
 -- Imports an xlsx sheet, converts it to a csv file, reads it, and checks the fields


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''
import sys
import pandas as pd
import datetime as dt
import xml.etree.ElementTree
from argparse import ArgumentParser, RawDescriptionHelpFormatter, Namespace


from os.path import os

aen_config_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), )) +
                  '/config/')

sys.path.append(aen_config_dir)
import fields as fields
from make_xlsx import Field

__all__ = []
__version__ = 0.1
__date__ = '2018-08-11'
__updated__ = '2018-08-11'

DEBUG = 1

def make_valid_dict():
    """
    Makes a dictionary of the possible fields with their validation.
    Does this by reading the fields list from the fields.py library

    Returns
    ---------
    field_dict : dict
        Dictionary of the possible fields
        Contains a Checker object under each name


    """

    field_dict = {}
    for field in fields.fields:
        field['name'] = field['name']
        print(field['name'])
        new = Checker(name=field['name'], disp_name=field['disp_name'])
        if 'valid' in field:
            new.set_validation(field['valid'])
        if 'inherit' in field:
            new.inherit = field['inherit']
        if 'units' in field:
            new.inherit = field['units']
#             print(new.validation)
        field_dict[field['name']] = new
    return field_dict


def xlsx_to_array(url,sheetname='Data',skiprows=2):
    """
    Convert xlsx to numpy 2D array of objects 
    
    Parameters
    ---------
    
    url: string
        The url to the xlsx file

    sheetname: str
        The sheet name for the sheet in the xlsx file wanted
        Default: 'Data'
    
    skiprows: int
        The numper of rows to skip 
        Default: 2

    Returns
    ---------
    
    data: numpy ndarray 
        A numpy ndarray of objects for the sheet. 
    """
    
    path = os.path.abspath(url)
    data = pd.read_excel(path,sheetname=sheetname, skiprows=skiprows).as_matrix()    
    
    # Convert Timestamps to dates
    return data

def get_validator(valid):
    """
    Checks a parameter according to the defined validation

    Parameters
    ---------

    valid: dict
        The valid dictionary defined in the fields.py file

    Returns
    ---------

    validator: lambda function
        A validator that takes one input, the value to be validated

    """
    validate = valid['validate'] 
    if validate == 'any':
        return lambda x: isinstance(x,str)
    elif validate == 'list':
        source = valid['source']
        return lambda x : x in source

    criteria = valid['criteria'] 
    def _formula_to_date(formula):

        form = formula.replace('=','')
        if 'TODAY()' in form:
            form =form.replace('TODAY()','dt.date.today()')
        if '+' in form:
            parts = form.split('+')
            parts[1] = 'dt.timedelta(days=' + parts[1] + ')'
            form = parts[0] + '+' + parts[1]
        elif '-' in form:
            parts = form.split('-')
            parts[1] = 'dt.timedelta(days=' + parts[1] + ')'
            form = parts[0] + '-' + parts[1]
        return eval(form)
    
    if validate == 'length':
        if criteria == 'between':
            return lambda x: valid['minimum'] <= len(x) <= valid['maximum']
        else:
            return lambda x: eval("len(x) "+ criteria + "valid['value']")
    elif validate == 'decimal':
        if criteria == 'between':
            return lambda x: valid['minimum'] <= float(x) <= valid['maximum']
        else:
            return lambda x: eval("float(x) "+ criteria + "valid['value']")
    elif validate == 'integer':
        if criteria == 'between':
            return lambda x: valid['minimum'] <= int(x) <= valid['maximum']
        else:
            return lambda x: eval("int(x) "+ criteria + "valid['value']")
    elif validate == 'time':
        if criteria == 'between':
            if isinstance(valid['minimum'],float) or isinstance(valid['minimum'],int):
                minimum = (dt.datetime(1,1,1,0,0)+dt.timedelta(days=valid['minimum'])).time()
                maximum = (dt.datetime(1,1,1,0,0)+dt.timedelta(days=valid['maximum'])).time()
            else:
                minimum = valid['minimum']
                maximum = valid['maximum']
            return lambda x: minimum <= x <= maximum
        else:
            if isinstance(valid['value'],float) or isinstance(valid['value'],int):
                limit =  (dt.datetime(1,1,1,0,0)+dt.timedelta(days=valid['value'])).time()
            else:
                limit = valid['value']
            return lambda x: eval("x"+ criteria + "limit")
    elif validate == 'date':
        if criteria == 'between':
            minimum = valid['minimum']
            maximum = valid['maximum']
            if not(isinstance(minimum,dt.date)):
                # We now have a fomula
                minimum = _formula_to_date(minimum) 
            if not(isinstance(maximum,dt.date)):
                # We now have a fomula
                minimum = _formula_to_date(maximum) 

            return lambda x: minimum <= x <= maximum
        else:
            limit =  valid['value']
            if not(isinstance(limit,dt.date)):
                # We now have a fomula
                limit = _formula_to_date(limit) 

            return lambda x: eval("x"+ criteria + "limit")



class Checker(Field):
    """
    Object for holding the specification of a cell, and the validation of it
    Inherits from Field""" 

    def __init__(self,inherit=False,units=None,*args,**kwargs):
        """
        Initialising the object
        
        Parameters
        ---------
        
        *args: arguments for Field

        **kwargs: keyword arguments for Field
        
        """
        Field.__init__(self,*args,**kwargs)                 
        if self.validation != {}:
            self.validator = get_validator(self.validation)
        else:
            self.validator = lambda x: True

        self.inherit = inherit
        self.units = units

    def set_validation(self,validation):
        Field.set_validation(self,validation)
        self.validator = get_validator(self.validation)



def check_value(value,field):
    valid = field['valid']
    validate = valid['validate'] 
    
    if validate == 'any':
        return isinstance(value,str) 
    if validate == 'length':
        if 'uuid' in field['name'].lower():
            try:
                uuid.UUID(value)
            except ValueError:
                raise ValueError("Field not a valid UUID")
        else:
            pass







#    sheet = workbook.add_worksheet('Metadata')

#    metadata_fields = ['title', 'abstract', 'pi_name', 'pi_email', 'pi_institution',
#                       'pi_address', 'recordedBy', 'projectID']




def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''
    try:
        args = parse_options()
        input = args.input
        field_list = make_valid_dict()

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0


def parse_options():
    """
    Parse the command line options and return these. Also performs some basic
    sanity checks, like checking number of arguments.
    """
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (
        program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

    Created by Pål Ellingsen on %s.

    Distributed on an "AS IS" basis without warranties
    or conditions of any kind, either express or implied.

    USAGE
''' % (program_shortdesc, str(__date__))

    # Setup argument parser
    parser = ArgumentParser(description=program_license,
                            formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0,
                        help="set verbosity level [default: %(default)s]")
    parser.add_argument('-V', '--version', action='version',
                        version=program_version_message)
    parser.add_argument(
        'input',  type=str, help="The input file to be processed")

    # Process arguments
    args = parser.parse_args()

    if args.verbose > 0:
        print("Verbose mode on")

    return args


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    sys.exit(main())

#!/usr/bin/python3
# encoding: utf-8
'''
 -- Imports an xlsx sheet, converts it to a csv file, reads it, and checks the fields


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''
import sys
import uuid
import pandas as pd
import numpy as np
import datetime as dt
import xml.etree.ElementTree
from xlrd import XLRDError
from argparse import ArgumentParser, RawDescriptionHelpFormatter, Namespace


from os.path import os

aen_config_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), )))

sys.path.append(aen_config_dir)
import config.fields as fields
from make_xlsx import Field

__all__ = []
__version__ = 0.1
__date__ = '2018-08-11'
__updated__ = '2018-08-11'

DEBUG = 1

REQUIERED = ['eventID', 
        'cruiseNumber',
        'stationName',
        'eventTime',
        'eventDate',
        'decimalLatitude',
        'decimalLongitude',
        'bottomDepthInMeters',
        'eventRemarks',
        'samplingProtocol',
        'parentEventID',
        'sampleLocation',
        'pi_name',
        'pi_email',
        'pi_institution',
        'recordedBy',
        'sampleType']


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
        # print(field['name'])
        new = Checker(name=field['name'], disp_name=field['disp_name'])
        if 'valid' in field:
            new.set_validation(field['valid'])
        if 'inherit' in field:
            new.inherit = field['inherit']
        if 'units' in field:
            new.units = field['units']
#             print(new.validation)
        field_dict[field['name']] = new
    return field_dict


def xlsx_to_array(url,sheetname='Data',skiprows=1):
    """
    Convert xlsx to numpy 2D array of objects 
    
    Parameters
    ---------
    
    url: string or io 
        Can either be a path or and io object

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
    
    if isinstance(url,str):

        url = os.path.abspath(url)
    data = pd.read_excel(url,sheetname=sheetname, skiprows=skiprows).as_matrix()    
        
        
    # Convert Timestamps to dates
    return data

def format_num(num):
    
    num_str = str(num).replace(',','.').replace("'",'')

    try:
        out = int(num_str)
    except ValueError:
        out = float(num_str)
    return out

def get_validator(valid):
    """
    Checks a parameter according to the defined validation

    Parameters
    ---------

    valid: dict
        The valid dictionary defined in the fields.py file

    Returns
    ---------

    validator: Evaluator
        A validator in the form of an Evaluator object

    """
    validate = valid['validate'] 
    if validate == 'any':
        return Evaluator(valid,func= lambda self,x: isinstance(str(x),str))
    elif validate == 'list':
        source = valid['source']
        return Evaluator(source, func=lambda self,x : str(x) in self.valid)

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
            return Evaluator(valid,func=lambda self,x: self.valid['minimum'] <= len(x) <= self.valid['maximum'])
        else:
            return Evaluator(valid,func = lambda self,x: eval("len(x) "+ self.valid['criteria'] + str(self.valid['value'])))
    elif validate == 'decimal':
        if criteria == 'between':
            return Evaluator(valid,func=lambda self,x: (isinstance(x,int) or isinstance(x,float)) and self.valid['minimum'] <= float(x) <= self.valid['maximum'])
        else:
            return Evaluator(valid, func=lambda self,x: (isinstance(x,int) or isinstance(x,float)) and eval("float(x) "+ self.valid['criteria'] + "self.valid['value']"))
    elif validate == 'integer':
        if criteria == 'between':
            return Evaluator(valid, func=lambda self,x: isinstance(x,int) and self.valid['minimum'] <= int(x) <= self.valid['maximum'])
        else:
            return Evaluator(valid, func=lambda self,x: isinstance(x,int) and eval("int(x) "+ self.valid['criteria'] + "int(self.valid['value'])"))
    elif validate == 'time':
        if criteria == 'between':
            if isinstance(valid['minimum'],float) or isinstance(valid['minimum'],int):
                minimum = (dt.datetime(1,1,1,0,0)+dt.timedelta(days=valid['minimum'])).time()
                maximum = (dt.datetime(1,1,1,0,0)+dt.timedelta(days=valid['maximum'])).time()
            else:
                minimum = valid['minimum']
                maximum = valid['maximum']
            ev = Evaluator(valid)
            ev.minimum = minimum
            ev.maximum = maximum
            ev.set_func(lambda self,x: self.minimum <= x <= self.maximum)
            return ev
        else:
            if isinstance(valid['value'],float) or isinstance(valid['value'],int):
                limit =  (dt.datetime(1,1,1,0,0)+dt.timedelta(days=valid['value'])).time()
            else:
                limit = valid['value']

            ev = Evaluator(valid)
            ev.limit = limit
            ev.set_func(lambda self,x: eval("x"+ self.valid['criteria']+ "self.limit"))
            return ev
    elif validate == 'date':
        # print("Date")
        if criteria == 'between':
            # print("Between")
            minimum = valid['minimum']
            maximum = valid['maximum']
            if not(isinstance(minimum,dt.date)):
                # We now have a fomula
                minimum = _formula_to_date(minimum) 
            if not(isinstance(maximum,dt.date)):
                # We now have a fomula
                maximum = _formula_to_date(maximum) 
            ev = Evaluator(valid)
            ev.minimum = minimum
            ev.maximum = maximum
            ev.set_func(lambda self,x: self.minimum <= x <= self.maximum)
            # ev.set_func(lambda self,x: print(self.minimum , x , self.maximum))
            return ev

        else:
            limit =  valid['value']
            if not(isinstance(limit,dt.date)):
                # We now have a fomula
                limit = _formula_to_date(limit) 

            ev = Evaluator(valid)
            ev.limit =limit
            
            ev.set_func(lambda self,x: eval("x"+ self.valid['criteria']+ "self.limit"))

            return ev
        # print(valid)
        raise NotImplementedError("No validator available for the object")

def is_nan(value):
    """
    Checks if value is 'nan'
    
    Parameters
    ---------
    
    value: object 
        The object to be checked that it is not nan
    
    Returns
    ---------
    
    isnan: Boolean 
        True: nan
        False: not nan
    """
    return str(value).lower() == 'nan'

    

class Evaluator(object):

    def __init__(self,valid,func=None):
        
        self.valid = valid
        if func != None:
            self.eval = func

    def set_func(self,func):
        self.eval = func

    def evaluate(self,value):
        return self.eval(self,value)


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



def check_value(value,checker):
    """
    Check the value with the checker.
    Does some additional checks in addition to the checks in checker
    
    Parameters
    ---------
    
    value: object
        The value to be checked

    checker: Checker
        The Checker to use
    
    Returns
    ---------
    
    bool : Boolean
        True, passed
        False, failed
    """
    
    if is_nan(value) or (isinstance(value,float) and np.isnan(value)):
        return True
    if checker.validation['validate'] == 'length':
        if 'eventid' in checker.name.lower():
            # print(value)
            try:
                uuid.UUID(value)
            except ValueError:
                return False
    if checker.validation['validate']=='date' and not(value.__class__ == dt.date(1,1,1).__class__):
        return checker.validator.evaluate(value.date())
    elif checker.validation['validate']=='integer' or checker.validation['validate']=='decimal'  :
        try:
            num = format_num(value)
        except ValueError:
            num = value 
        return checker.validator.evaluate(num)
    else:
        return checker.validator.evaluate(value)

def check_array(data,checker_list,skiprows):
    """
    Checks the data according to the validators in the checker_list
    Returns True if the data is good, as well as an empty string
    
    Parameters
    ---------
    
    data : numpy ndarray of objects
        The data to be checked.
        The first row should contain the names of the fields as specified in fields.py
    
    checker_list : dict of Checker objects
        This is a list of the possible checkers made by make_valid_dict 

    skiprows: int
        The number of rows skipped when reading in the data with pandas
        If something else is used this should be 1 less, as pandas skips one row
        This is needed to give the excel reference correct

    Returns
    ---------
    
    good : Boolean
        A boolean specifying if the data passed the checks (True)

    errors: list of strings
        A string per error, describing where the error was found
        On the form: paramName: disp_name : row
    """
    good = True
    errors = []
    # Check that every cell is correct
    evID = np.where(data[0,:]=='eventID')[0][0]
    pID = np.where(data[0,:]=='parentEventID')[0][0]

    for col in range(data.shape[1]):
        if is_nan(data[0,col]):
            continue
        # print(data[0,col])
        try : 
            checker = checker_list[data[0,col]] 
        except KeyError:
            good = False
            errors.append("Column name not known, Row: 3, value: "+ str(data[0,col]))
            continue
        rows = []
        missing = []
        req = checker.name in REQUIERED
        # Checking type
        for row in range(1,data.shape[0]):
            if not(check_value(data[row,col],checker)):
                if good:
                    errors.append("Content errors")
                good = False
                rows.append(row+skiprows+2)
            if req and is_nan(data[row,col]):
                if not(is_nan(data[row,evID])):
                    if checker.inherit and is_nan(data[row,pID]):
                        missing.append(row+skiprows+2)
        if rows !=[]:        
            errors.append(checker.disp_name + ' ('+checker.name +')'+", Rows: "+ to_ranges_str(rows) + ' Error: Content in wrong format' )
        if missing !=[]:
            errors.append(checker.disp_name + ' ('+checker.name +')'+", Rows: "+ to_ranges_str(missing) + ' Error: Required value missing (parent UUID missing?)' )

    # Check that the uuids in eventID are unique
    if 'eventID' in data[0,:]:
        index = np.where(data[0,:]=='eventID')[0][0]
        ind = pd.Index(data[1:,index].astype(np.str))
        if ind.has_duplicates:
            # We have found dupes
            dups = ind.get_duplicates()
            first = True
            for dup in dups:
                if not(is_nan(dup)):
                    if first:
                        first = False
                        errors.append('Duplicate uuids in eventID (sampleID)')
                    errors.append("Rows: "+to_ranges_str((ind.get_indexer_for([dup])+skiprows+3).tolist()) + ', UUID: '+dup)
                    good = False

    return good, errors

def to_ranges_str(lis):
    out = '['+str(lis[0])
    if len(lis)==2:
       out = out + ', ' + str(lis[1])
    elif len(lis)>2:
        first = lis[0]
        prev = first 
        ii=1
        for l in lis[1:]:
            
            if l==prev+1:
                prev =l
                ii=ii+1
            else:
                # longer step
                if ii>2:
                    out = out+ ' - ' +str(prev)
                else:
                    out = out +', '+str(prev)
                prev = l
                first = l
                out = out + ', ' + str(first)
                ii=0
        if ii>2:
            out = out+ ' - ' +str(prev)
        else:
            out = out +', '+str(prev)
        

    out = out + ']'
    return out    

                







#    sheet = workbook.add_worksheet('Metadata')

#    metadata_fields = ['title', 'abstract', 'pi_name', 'pi_email', 'pi_institution',
#                       'pi_address', 'recordedBy', 'projectID']


def prune(data):
    """
    Remove columns without the identifier (first row) as these are non standard rows
    
    Parameters
    ---------
    
    data: numpy ndarray of objects
        The data to be pruned. 
        
    
    Returns
    ---------
    
    data: numpy ndarray of objects
        The pruned data
    """
    return data[:,data[0,:]!=''] 

def clean(data):
    """
    Goes through the array and cleans up the data
    Fixes some numbers that have not been converted correctly
    Converts uuids to lower and makes sure seperator is '-' and not '+' '/'
    
    Parameters
    ---------
    
    data: nunpy ndarray of objects
        The data to be cleaned, first row should be the header row
    
    Returns
    ---------
   
    cleaned_data: numpy ndarray of objects
        The cleaned data
    
    """
    cleaned_data = np.copy(data) 
    for col in range(data.shape[1]):
        name = data[0,col]
        for row in range(1,data.shape[0]):
            if 'eventid' in name.lower() and not(is_nan(data[row,col])):
                cleaned_data[row,col] = data[row,col].replace('+','-').replace('/','-')
            else:
                try:
                    num = format_num(data[row,col])
                    cleaned_data[row,col]=num
                except ValueError:
                    continue 

    return cleaned_data
    

def run(input):
    checker_list = make_valid_dict()
    # Read in data and prune of custom columns
    skiprows = 1
    try:
        data = prune(xlsx_to_array(input,skiprows=1))
        data = clean(data)
    except XLRDError: 
        return False, ["Does not contain the 'Data' sheet. Is this the correct file?"]
    return check_array(data, checker_list, skiprows)

def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''
    try:
        args = parse_options()
        input = args.input
        print(run(input))    
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

#!/usr/bin/python3
# encoding: utf-8
'''
 -- Creates xlsx files for collecting samples for Biology in Nansen Legacy


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''
import sys
import xlsxwriter
import xml.etree.ElementTree
from argparse import ArgumentParser, RawDescriptionHelpFormatter, Namespace

from os.path import os

aen_config_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), )) +
                  '/config/')

sys.path.append(aen_config_dir)
import fields as fields

__all__ = []
__version__ = 0.1
__date__ = '2018-05-22'
__updated__ = '2018-07-05'

DEBUG = 1

DEFAULT_FONT = 'Calibri'
DEFAULT_SIZE = 10


class Field(object):
    """
    Object for holding the specification of a cell

    """

    def __init__(self, name, disp_name, validation={},
                 cell_format={}, width=20, long_list=False):
        """
        Initialising the object

        Parameters
        ----------
        name : str
               Name of object

        disp_name : str
               The title of the column

        validation : dict, optional
            A dictionary using the keywords defined in xlsxwriter

        cell_format : dict, optional
            A dictionary using the keywords defined in xlsxwriter

        width : int, optional
            Number of units for width

        long_list : Boolean, optional
            True for enabling the long list.
        """
        self.name = name  # Name of object
        self.disp_name = disp_name  # Title of column
        self.cell_format = cell_format  # For holding the formating of the cell
        self.validation = validation  # For holding the validation of the cell
        self.long_list = long_list  # For holding the need for an entry in the
        # variables sheet
        self.width = width

    def set_validation(self, validation):
        """
        Set the validation of the cell

        Parameters
        ----------
        validation : dict
            A dictionary using the keywords defined in xlsxwriter

        """
        self.validation = validation

    def set_cell_format(self, cell_format):
        """
        Set the validation of the cell

        Parameters
        ----------
        cell_format : dict
            A dictionary using the keywords defined in xlsxwriter

        """
        self.cell_format = cell_format

    def set_width(self, width):
        """
        Set the cell width

        Parameters
        ----------
        width : int
            Number of units for width


        """
        self.width = width

    def set_long_list(self, long_list):
        """
        Set the need for moving the source in the list to a cell range in the
        variables sheet

        Parameters
        ----------
        long_list : Boolean
            True for enabling the long list.


        """
        self.long_list = long_list


class Variable_sheet(object):
    """
    Class for handling the variable sheet

    """

    def __init__(self, workbook):
        """
        Initialises the sheet

        Parameters
        ----------
        workbook: Xlsxwriter workbook
            The parent workbook where the sheet is added

        """
        self.workbook = workbook
        self.name = 'Variables'  # The name of the worksheet
        self.sheet = workbook.add_worksheet(self.name)
        self.sheet.hide()  # Hide the sheet
        # For holding the current row to add variables on
        self.current_column = 0

    def add_row(self, variable, parameter_list):
        """
        Adds a row of parameters to a variable and returns the ref for the list

        Parameters
        ----------
        variable : str
            The name of the variable

        parameter_list : 
            List of paramters to be added

        Returns
        ----------
        ref : str
            The range of the list in Excel format
        """

#         print(parameter_list)
        self.sheet.write(0, self.current_column, variable)
        name = 'Table_' + variable.replace(' ', '_').capitalize()

        tab = self.sheet.add_table(
            1, self.current_column,
            1 + len(parameter_list), self.current_column,
            {'name': name,
                'header_row': 0}
        )
#         print(tab.properties['name'])
        #

        for ii, par in enumerate(sorted(parameter_list, key=str.lower)):
            self.sheet.write(1 + ii, self.current_column, par)
        ref = '=INDIRECT("' + name + '")'

        # Increment row such that the next gets a new row
        self.current_column = self.current_column + 1
        return ref


def make_dict_of_fields():
    """
    Makes a dictionary of the possible fields.
    Does this by reading the fields list from the fields.py library

    Returns
    ---------
    field_dict : dict
        Dictionary of the possible fields
        Contains a Field object under each name


    """

    field_dict = {}
    for field in fields.fields:
        field['name'] = field['name']
        new = Field(field['name'], field['disp_name'])
        if 'valid' in field:
            new.set_validation(field['valid'])
#             print(new.validation)
        if 'cell_format' in field:
            new.set_cell_format(field['cell_format'])
        if 'width' in field:
            new.set_width(field['width'])
        else:
            new.set_width(len(field['disp_name']))
        if 'long_list' in field:
            new.set_long_list(field['long_list'])

        field_dict[field['name']] = new
    return field_dict


def read_xml(args, xmlfile):
    """
    Read the XML file containing the definition of the wanted output xlsx files

    Parameters
    ----------
    args : argparse object
        The input args

    xmlfile : str
        The xml file to be read

    Returns
    ----------
    files : list
        List of dictionaries with the file specifications
    """

    files = []

    e = xml.etree.ElementTree.parse(xmlfile).getroot()
    if args.verbose > 0:
        print("Reading")
    for file in e.findall('file'):
        new = {}
        new['name'] = file.attrib['name']
        new['disp_name'] = file.find('disp_name').text
        new['fields'] = [
            child.text for child in file.find('fields').getchildren()]

        files.append(new)
    return files


def write_metadata(args, workbook, field_dict):
    """
    Adds a metadata sheet to workbook

    Parameters
    ----------
    args : argparse object
        The input arguments

    workbook : xlsxwriter Workbook
        The workbook for the metadata sheet

    field_dict : dict
        Contains a dictionary of Field objects and their name, made with 
        make_dict_of _fields()

    """

    sheet = workbook.add_worksheet('Metadata')

    metadata_fields = ['title', 'abstract', 'pi_name', 'pi_email', 'pi_institution',
                       'pi_address', 'recordedBy', 'projectID']

    parameter_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'right': True,
        'bottom': True,
        'bold': False,
        'text_wrap': True,
        'valign': 'left',
        'font_size': DEFAULT_SIZE + 2,
        'bg_color': '#B9F6F5',
    })
    input_format = workbook.add_format({
        'bold': False,
        'font_name': DEFAULT_FONT,
        'text_wrap': True,
        'valign': 'left',
        'font_size': DEFAULT_SIZE
    })

    heigth = 15
    sheet.set_column(0, 0, width=30)
    sheet.set_column(2, 2, width=50)
    for ii, mfield in enumerate(metadata_fields):
        field = field_dict[mfield]
        sheet.write(ii, 0, field.disp_name, parameter_format)
        sheet.write(ii, 1, field.name, parameter_format)
        sheet.set_column(1, 1, None, None, {'hidden': True})
        sheet.write(ii, 2, '', input_format)
        sheet.set_row(ii, heigth)
        if field.validation:
            if args.verbose > 0:
                print("Writing metadata validation")
            valid_copy = field.validation.copy()
            if len(valid_copy['input_message']) > 255:
                valid_copy['input_message'] = valid_copy[
                    'input_message'][:252] + '...'
            sheet.data_validation(first_row=ii,
                                  first_col=1,
                                  last_row=ii,
                                  last_col=1,
                                  options=valid_copy)
            if field.cell_format:
                cell_format = workbook.add_format(field.cell_format)
                sheet.set_row(
                    ii, ii, cell_format=cell_format)


def make_xlsx(args, file, field_dict):
    """
    Writes the xlsx file based on the the wanted fields

    Parameters
    ----------
    args : argparse object
        The input arguments

    file : dict
        The definition of the file wanted, generate this with read_xml

    field_dict : dict
        Contains a dictionary of Field objects and their name, made with 
        make_dict_of _fields()

    """

    output = os.path.join(args.dir, file['name'] + '.xlsx')
    workbook = xlsxwriter.Workbook(output)

    # Set font
    workbook.formats[0].set_font_name(DEFAULT_FONT)
    workbook.formats[0].set_font_size(DEFAULT_SIZE)

    write_metadata(args, workbook, field_dict)
    # Create sheet for data
    data_sheet = workbook.add_worksheet('Data')
    variable_sheet_obj = Variable_sheet(workbook)

    header_format = workbook.add_format({
        #         'bg_color': '#C6EFCE',
        'font_name': DEFAULT_FONT,
        'bold': False,
        'text_wrap': False,
        'valign': 'vcenter',
        #         'indent': 1,
        'font_size': DEFAULT_SIZE + 2
    })

    field_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'bottom': True,
        'right': True,
        'bold': False,
        'text_wrap': True,
        'valign': 'vcenter',
        'font_size': DEFAULT_SIZE + 1,
        'bg_color': '#B9F6F5'
    })

    title_row = 1  # starting row
    start_row = title_row + 2
    parameter_row = title_row + 1  # Parameter row, hidden
    end_row = 20000  # ending row

    for ii in range(len(file['fields'])):  # Loop over all the variables needed
        # Get the wanted field object
        field = field_dict[file['fields'][ii]]

        # Write title row
        data_sheet.write(title_row, ii, field.disp_name, field_format)

        # Write row below with parameter name
        data_sheet.write(parameter_row, ii, field.name)
        # Write validation
        if field.validation is not None:
            if args.verbose > 0:
                print("Writing validation for", file['fields'][ii])

            if field.long_list:
                # We need to add the data to the validation sheet
                # Copying the dict as we need to modify it
                valid_copy = field.validation.copy()

                # Add the validation variable to the hidden sheet
                ref = variable_sheet_obj.add_row(
                    field.name, valid_copy['source'])
                valid_copy.pop('source', None)
                valid_copy['value'] = ref
                data_sheet.data_validation(first_row=start_row,
                                           first_col=ii,
                                           last_row=end_row,
                                           last_col=ii,
                                           options=valid_copy)
            else:
                # Need to make sure that 'input_message' is not more than 255
                valid_copy = field.validation.copy()
                if len(valid_copy['input_message']) > 255:
                    valid_copy['input_message'] = valid_copy[
                        'input_message'][:252] + '...'
                data_sheet.data_validation(first_row=start_row,
                                           first_col=ii,
                                           last_row=end_row,
                                           last_col=ii,
                                           options=valid_copy)
        if field.cell_format is not None:
            if not('font_name' in field.cell_format):
                field.cell_format['font_name'] = DEFAULT_FONT
            if not('font_size' in field.cell_format):
                field.cell_format['font_size'] = DEFAULT_SIZE
            cell_format = workbook.add_format(field.cell_format)
            data_sheet.set_column(
                ii, ii, width=field.width, cell_format=cell_format)
        else:
            data_sheet.set_column(first_col=ii, last_col=ii, width=field.width)

    # Add header, done after the other to get correct format
    data_sheet.write(0, 0, file['disp_name'], header_format)

    data_sheet.set_row(0, height=24)

    # Freeze the rows at the top
    data_sheet.freeze_panes(start_row, 0)

    # Hide ID row
    data_sheet.set_row(parameter_row, None, None, {'hidden': True})

    # Colour the rows alternating
#     row_col = workbook.add_format({'bg_color': '#F7FFFF'})
#
#     for row in range(start_row, int(end_row / 100), 2):
#         data_sheet.set_row(row, cell_format=row_col)
#         worksheet.write(row, 0, '')
    workbook.close()


def write_file(url, fields, field_dict):
    """
    Method for calling from other python programs

    Parameters
    ----------
    url: string
        The output file

    fields : list
        A list of the wanted fields

    fields: dict
        A list of the wanted fields on the format shown in config.fields

    """
    args = Namespace()
    args.verbose = 0
    args.dir = os.path.dirname(url)
    file = {'name': os.path.basename(url).split('.')[0],
            'disp_name': 'Enter measurement type',
            'fields': fields}

    make_xlsx(args, file, field_dict)


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''
    try:
        args = parse_options()
        xmlfile = args.input
    #         save_pages(output, N=args.n)

        files = read_xml(args, xmlfile)
        for file in files:
            if args.verbose > 0:
                print("Writing file", file['disp_name'])
            field_list = make_dict_of_fields()
            make_xlsx(args, file, field_list)

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
        '-d', dest='dir', default='', type=str, help="Set the optput directory, [default: %(default)s]")
    parser.add_argument('-i', dest='input', default=os.path.join(os.path.dirname(
        sys.argv[0]), 'config', 'files.xml'), help='''The input xml file, [default: %(default)s]"''')

    # Process arguments
    args = parser.parse_args()

    if args.verbose > 0:
        print("Verbose mode on")

    return args


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    sys.exit(main())

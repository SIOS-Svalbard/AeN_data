#!/usr/bin/python3
# encoding: utf-8
'''
 -- Creates xlsx files for collecting samples for Biology in Nansen Legacy


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''
import config.fields as fields
import sys
import xlsxwriter
import xml.etree.ElementTree
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os.path import os

__all__ = []
__version__ = 0.1
__date__ = '2018-05-22'
__updated__ = '2018-05-31'
DEBUG = 1


class Field(object):
    """
    Object for holding the specification of a cell

    """

    def __init__(self, name, disp_name):
        """
        Initialising the object

        Parameters
        ----------
        name : str
               The name of the cell column
        """
        self.name = name  # Name of object
        self.disp_name = disp_name  # Title of column
        self.cell_format = None  # For holding the formating of the cell
        self.validation = None  # For holding the validation of the cell
        self.width = 20

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
        new = Field(field['name'], field['disp_name'])
        if 'valid' in field:
            new.set_validation(field['valid'])
#             print(new.validation)
        if 'cell_format' in field:
            new.set_cell_format(field['cell_format'])
        if 'width' in field:
            new.set_width(field['width'])

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
            child.text.lower() for child in file.find('fields').getchildren()]

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
                       'pi_address', 'project_long',
                       'project_short']

    parameter_format = workbook.add_format({
        'right': True,
        'bold': True,
        'text_wrap': True,
        'valign': 'left',
        'indent': 1,
        'font_size': 12
    })
    input_format = workbook.add_format({
        'bold': False,
        'text_wrap': True,
        'valign': 'left',
        'indent': 1
    })

    heigth = 15
    sheet.set_column(0, 0, width=30)
    sheet.set_column(1, 1, width=50)
    for ii, mfield in enumerate(metadata_fields):
        field = field_dict[mfield]
        sheet.write(ii, 0, field.disp_name, parameter_format)
        sheet.write(ii, 1, '', input_format)
        sheet.set_row(ii, heigth)
        if field.validation is not None:
            if args.verbose > 0:
                print("Writing metadata validation")
            sheet.data_validation(first_row=ii,
                                  first_col=1,
                                  last_row=ii,
                                  last_col=1,
                                  options=field.validation)
            if field.cell_format is not None:
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

    write_metadata(args, workbook, field_dict)
    # Create sheet for data
    data_sheet = workbook.add_worksheet('Data')

    header_format = workbook.add_format({
        #         'bg_color': '#C6EFCE',
        'bold': True,
        'text_wrap': False,
        'valign': 'vcenter',
        'indent': 1,
        'font_size': 12
    })

    field_format = workbook.add_format({
        'bottom': True,
        'bold': True,
        'text_wrap': True,
        'valign': 'vcenter',
        'indent': 1,
    })

    title_row = 3  # starting row
    start_row = title_row + 1
    end_row = 20000  # ending row

    for ii in range(len(file['fields'])):  # Loop over all the variables needed
        field = field_dict[file['fields'][ii]]  # Get the wanted field object

        # Write title row
        data_sheet.write(title_row, ii, field.disp_name, field_format)
        if field.validation is not None:
            if args.verbose > 0:
                print("Writing validation for", file['fields'][ii])
            data_sheet.data_validation(first_row=start_row,
                                       first_col=ii,
                                       last_row=end_row,
                                       last_col=ii,
                                       options=field.validation)
        if field.cell_format is not None:
            cell_format = workbook.add_format(field.cell_format)
            data_sheet.set_column(
                ii, ii, width=field.width, cell_format=cell_format)
        else:
            data_sheet.set_column(first_col=ii, last_col=ii, width=field.width)

    # Add header, done after the other to get correct format
    data_sheet.write(0, 0, 'Measurement', header_format)
    data_sheet.merge_range(0, 1, 0, 2, file['disp_name'], header_format)

    data_sheet.write(1, 0, 'Name', header_format)
    data_sheet.merge_range(1, 1, 1, 2, '', header_format)

    data_sheet.set_row(0, height=24)
    data_sheet.set_row(1, height=24)

    workbook.close()


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

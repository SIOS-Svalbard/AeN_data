#! /usr/bin/env python3
# encoding: utf-8
'''
 -- Inserts data from xlsx sheets into database


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''

__all__ = []
__version__ = 0.2
__date__ = '2018-09-12'
__updated__ = '2019-06-04'

import psycopg2
import psycopg2.extras
import uuid
import darwinsheet.scripts.process_xlsx as px
import datetime as dt
import getpass
import glob
import sys
import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import numpy as np
import datetime as dt
from collections import OrderedDict
from psycopg2 import sql


# columns = {"parentEventID": "uuid",
# "cruiseNumber": "int",
# "stationName": "text",
# "eventTime": "time",
# "eventDate": "date",
# "decimalLatitude": "double precision",
# "decimalLongitude": "double precision",
# "bottomDepthInMeters": "double precision",
# "eventRemarks": "text",
# "samplingProtocol": "text",
# "sampleLocation": "text",
# "pi_name": "text",
# "pi_email": "text",
# "pi_institution": "text",
# "recordedBy": "text",
# "sampleType": "text",
# "other": "hstore",
# "metadata": "hstore",
# "created": "timestamp with time zone",
# "modified": "timestamp with time zone",
# "history": "text",
# "source": "text"}

REQUIERED = ["eventID",
             "parentEventID",
             "cruiseNumber",
             "stationName",
             "eventTime",
             "eventDate",
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

COLUMNS = ["eventID",
           "parentEventID",
           "cruiseNumber",
           "stationName",
           "eventTime",
           "eventDate",
           "decimalLatitude",
           "decimalLongitude",
           "sampleType",
           "gearType",
           "sampleDepthInMeters",
           "bottomDepthInMeters",
           "bottleNumber",
           "samplingProtocol",
           "sampleLocation",
           "pi_name",
           "pi_email",
           "pi_institution",
           "recordedBy",
           "eventRemarks"]


def to_dict(keys, values):
    '''
    Create dictionary from keys and values

    Parameters
    ----------
    keys: list of str
        A list of the keys for the dictionary

    values: list of str
        A list of the values for the keys in the dictionary

    Returns
    ----------
    met: dict
        The resulting dictionary from the keys and values
    '''
    met = {}
    for r in range(len(keys)):
        if px.is_nan(values[r]):
            continue
        else:
            met[keys[r]] = str(values[r])

    return OrderedDict(sorted(met.items(), key=lambda t: t[0]))


def find_missing(seq, num):
    '''
    Find the values not present in a sequence 

    Parameters
    ----------
    seq: list of int
        The sequence of int 

    num: int
        The length of the wanted sequence from 0 to num

    Returns
    ----------
    miss: list of int
        The missing integers in "seq" from the range(0,num)
    '''
    return sorted(set(range(0, num)).difference(sorted(seq)))


def replace_nan(lis):
    '''
    Replace NaNs in a list with None

    Parameters
    ----------
    lis: list
        The list containing NaNs

    Returns
    ----------
    new: list
        The list with NaNs replaced by None
    '''
    new = []
    for l in lis:
        if px.is_nan(l):
            new.append(None)
        else:
            new.append(l)
    return new


def trim_str(lis):
    '''
    Strip extra spaces from the members in the list 

    Parameters
    ----------
    lis: list
        The list to be stripped 

    Returns
    ----------
    new: list
        The new list with extra white spaces stripped
    '''
    new = []
    for l in lis:
        if isinstance(l, str):
            new.append(l.strip())
        else:
            new.append(l)
    return new


def get_time_now():
    '''
    Returns the time now in iso8601 format

    Returns
    ----------
    time_now : str
        The time now in iso8601 format
    '''
    return dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def insert_db(cur, data, metadata, filename, update=False, reason=''):
    '''
    This inserts the data into the database, alternatively updates the fields

    Parameters
    ----------
    cur : psycopg2 cursor
        Database cursor

    data : data array
        the data to be inserted with header for every column

    metadata : array
        The metadata to be inserted

    filename : str
        The source filename

    update : Boolean, optional
        Determines if fields are updated.
        Default: False

    reason : str, optional
        Reason for update
        Default: ''

    '''
    try:
        meta = to_dict(metadata[:, 0], metadata[:, 1])
    except IndexError:
        meta = {}
    # print(meta)
    stat = ""
    fields = ""
    fields_up = ""  # For update statement
    indxs = []
    exists_query = '''
    select exists(
        select 1
        from aen
        where eventid= %s
    )'''

    for r in COLUMNS:
        if any(data[0, :] == r):
            indxs.append(np.where(data[0, :] == r)[0][0])
            fields = fields + r + ", "
            if r != COLUMNS[0]:  # Don't insert eventid in fields_up
                fields_up = fields_up + r + "=%s, "
            stat = stat + "%s,"

    o_indxs = find_missing(indxs, data.shape[1])

    stat = stat + "%s,%s,%s,%s,%s,%s"  # For the other and metadata
    fields = fields + "other, metadata, created, modified, history, source"
    fields_up = fields_up + \
        "other = other || %s , metadata = metadata || %s, modified = %s, history = %s, source = %s"

    for r in range(1, data.shape[0]):
        row = []
        cols = data[r, indxs].tolist()
        cols = replace_nan(cols)
        cols = trim_str(cols)
        cols.append(to_dict(data[0, o_indxs], data[r, o_indxs]))
        cols.append(meta)
        if cols[0] == None:
            continue
        cur.execute(exists_query, (cols[0],))
        exists = cur.fetchone()[0]
        query3 = sql.SQL("SELECT history from aen where eventid = %s")
        if not(exists):
            created = get_time_now()
            cols.append(created)  # Created
            cols.append(created)  # Modified
            # History
            cols.append(created + ": Initial read in of the log files.")
            cols.append(filename)  # Source file

            cur.execute(
                "INSERT INTO aen (" + fields + ") VALUES(" + stat + ")", cols)
        elif update:

            # Need to extract created and history
            modified = get_time_now()
            cur.execute(query3, (cols[0],))
            history = cur.fetchone()[0]
            if reason == '':
                print("What is the reason for the update (is appended to the history):")
                mod_message = input()
                print("Should this be kept for the file? [y/n]")
                answer = input().lower()
                if answer == 'y':
                    reason = mod_message
            else:
                mod_message = reason
            history = history+"\n" + modified+": " + mod_message
            cols.append(modified)  # Modified
            cols.append(history)  # History
            cols.append(filename)  # Source file
            # update everything except eventid
            temp = cols.copy()
            temp.append(temp[0])
            cur.execute(
                "UPDATE aen set " + fields_up + " where eventid = %s", temp[1:])
        else:
            print("Skipping due to duplicate id " + cols[0])
            continue


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''
    try:
        args = parse_options()
        files = args.input
        # Connect to the database as the user running the script
        conn = psycopg2.connect('dbname=aen_db user=' + getpass.getuser())
        psycopg2.extras.register_uuid()
        psycopg2.extras.register_hstore(conn)

        cur = conn.cursor()

        if os.path.isfile(files):
            urls = []
            urls.append(files)
        else:
            urls = glob.glob(os.path.join(files, '*.xlsx'))

        for url in urls:
            print("Url", url)

            good, error, data, metadata = px.run(url, return_data=True)

            if not(good):
                print("Errors found")
                for line in error:
                    print(line)
                print("Should we continue? [y/n]")
                answer = input().lower()
                if answer != 'y':
                    continue
            filename = os.path.basename(url)
            insert_db(cur, data, metadata, filename, args.update, args.mod)

        conn.commit()
        cur.close()
        conn.close()
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

    parser.add_argument(
        'input', type=str, help='''The input file or folder with the xlsx files''')
    # parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0,
    #                     help="set verbosity level [default: %(default)s]")
    parser.add_argument('-V', '--version', action='version',
                        version=program_version_message)
    parser.add_argument('-u', dest='update', default=False, action="store_true",
                        help="Update entries. If enabled existing entries will be updated, [default: %(default)s]")
    parser.add_argument('-m', dest='mod', default='', type=str,
                        help="Set the modification message if updating. [Default: %(default)s]")

    # Process arguments
    args = parser.parse_args()

    # if args.verbose > 0:
    #     print("Verbose mode on")

    return args


if __name__ == "__main__":
    sys.exit(main())

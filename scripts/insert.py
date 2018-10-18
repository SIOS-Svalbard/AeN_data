#! /usr/bin/env python3
# encoding: utf-8
'''
 -- Insertes data from xlsx sheets into database


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''

__all__ = []
__version__ = 0.2
__date__ = '2018-09-12'
__updated__ = '2018-10-03'

import psycopg2
import psycopg2.extras
import uuid
import process_xlsx as px
import datetime as dt
import glob
import sys
import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import numpy as np
from collections import OrderedDict
from psycopg2 import sql


columns = {"parentEventID": "uuid",
           "cruiseNumber": "int",
           "stationName": "text",
           "eventTime": "time",
           "eventDate": "date",
           "decimalLatitude": "double precision",
           "decimalLongitude": "double precision",
           "bottomDepthInMeters": "double precision",
           "eventRemarks": "text",
           "samplingProtocol": "text",
           "sampleLocation": "text",
           "pi_name": "text",
           "pi_email": "text",
           "pi_institution": "text",
           "recordedBy": "text",
           "sampleType": "text",
           "other": "hstore",
           "metadata": "hstore"}

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
exe_str = '''
CREATE TABLE aen (eventID uuid PRIMARY KEY,
                              parentEventID uuid,
                              cruiseNumber int,
                              stationName text,
                              eventTime time,
                              eventDate date,
                              decimalLatitude double precision,
                              decimalLongitude double precision,
                              sampleType text,
                              gearType text,
                              sampleDepthInMeters double precision,
                              bottomDepthInMeters double precision,
                              bottleNumber integer,
                              samplingProtocol text,
                              sampleLocation text,
                              pi_name text,
                              pi_email text,
                              pi_institution text,
                              recordedBy text,
                              eventRemarks text,
                              other hstore,
                              metadata hstore) '''


def to_dict(keys, values):
    met = {}
    for r in range(len(keys)):
        if px.is_nan(values[r]):
            continue
        else:
            met[keys[r]] = str(values[r])

    return OrderedDict(sorted(met.items(), key=lambda t: t[0]))


def find_missing(seq, num):
    return sorted(set(range(0, num)).difference(sorted(seq)))


def replace_nan(lis):
    new = []
    for l in lis:
        if px.is_nan(l):
            new.append(None)
        else:
            new.append(l)
    return new


def insert_db(cur, data, metadata, update=False):
    try:
        meta = to_dict(metadata[:, 0], metadata[:, 1])
    except IndexError:
        meta = {}
    # print(meta)
    stat = ""
    fields = ""
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
            stat = stat + "%s,"

    o_indxs = find_missing(indxs, data.shape[1])

    stat = stat + "%s,%s"  # For the other and metadata
    fields = fields + "other, metadata"

    for r in range(1, data.shape[0]):
        row = []
        cols = data[r, indxs].tolist()
        cols = replace_nan(cols)
        cols.append(to_dict(data[0, o_indxs], data[r, o_indxs]))
        cols.append(meta)
        if cols[0] == None:
            continue
        cur.execute(exists_query, (cols[0],))
        exists = cur.fetchone()[0]
        query2 = sql.SQL("DELETE from aen where eventid = %s")
        if not(exists):
            cur.execute(
                "INSERT INTO aen (" + fields + ") VALUES(" + stat + ")", cols)
        elif update:
            cur.execute(query2,(cols[0],))
            cur.execute(
                "INSERT INTO aen (" + fields + ") VALUES(" + stat + ")", cols)
        else:
            print("Skipping due to duplicate id " + cols[0])
            continue

def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''
    try:
        args = parse_options()
        files = args.input
        conn = psycopg2.connect("dbname=test user=pal")
        psycopg2.extras.register_uuid()
        psycopg2.extras.register_hstore(conn)

        cur = conn.cursor()

        if args.init:
            cur.execute("CREATE EXTENSION hstore;")
            cur.execute(exe_str)

        conn.commit()
        if os.path.isfile(files):
            urls = []
            urls.append(files)
        else:
            urls = glob.glob(os.path.join(files,'*.xlsx'))

        for url in urls:
            print("Url",url)

            good, error, data, metadata = px.run(url, return_data=True)

            if not(good):
                print("Errors found")
                for line in error:
                    print(line)
                print("Should we continue? [y/n]")
                answer = input().lower()
                if answer != 'y':
                    continue
            insert_db(cur, data, metadata, args.update)


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

    parser.add_argument('input',type=str, help='''The input file or folder with the xlsx files''')
    # parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0,
    #                     help="set verbosity level [default: %(default)s]")
    parser.add_argument('-V', '--version', action='version',
                        version=program_version_message)
    parser.add_argument('-u', dest='update', default=False, action="store_true", help="Update entries. If enabled existing entries will be updated, [default: %(default)s]")
    parser.add_argument('-i', dest='init', default=False, action="store_true", help="Initialise the database. [Default: %(default)s]")


    # Process arguments
    args = parser.parse_args()

    # if args.verbose > 0:
    #     print("Verbose mode on")

    return args


if __name__ == "__main__":
    sys.exit(main())

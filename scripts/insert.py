#! /usr/bin/env python3
import psycopg2
import psycopg2.extras
import uuid
import process_xlsx as px
import datetime as dt
import glob
import numpy as np
from collections import OrderedDict

conn = psycopg2.connect("dbname=test user=pal")
cur = conn.cursor()

# cur.execute("CREATE EXTENSION hstore;")

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
# cur.execute(exe_str)
psycopg2.extras.register_uuid()
psycopg2.extras.register_hstore(conn)
conn.commit()


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


def insert_db(cur, data, metadata):
    meta = to_dict(metadata[:, 0], metadata[:, 1])
    print(meta)
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
        if not(exists):
            cur.execute(
                "INSERT INTO aen (" + fields + ") VALUES(" + stat + ")", cols)
        else:
            print("Skipping due to duplicate id " + cols[0])
            continue

    #    sheet = workbook.add_worksheet('Metadata')


    #    metadata_fields = ['title', 'abstract', 'pi_name', 'pi_email', 'pi_institution',
    #                       'pi_address', 'recordedBy', 'projectID']
urls = glob.glob(
    "/home/pal/Documents/AeN/Cruise/2018707/SAMPLE LOGS/Corrected/*.xlsx")

for url in urls:
    print(url)

    good, error, data, metadata = px.run(url, return_data=True)

    if not(good):
        print("Errors found")
        for line in error:
            print(line)
        print("Should we continue? [y/n]")
        answer = input().lower()
        if answer != 'y':
            continue
    insert_db(cur, data, metadata)


conn.commit()
cur.close()
conn.close()

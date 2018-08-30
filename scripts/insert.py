#! /usr/bin/env python3
import psycopg2
import psycopg2.extras
import uuid
import process_xlsx as px
import numpy as np
import datetime as dt


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

# cur.execute(
# "CREATE TABLE aen (eventID uuid PRIMARY KEY, parentEventID uuid, cruiseNumber int, stationName text, eventTime time, eventDate date, decimalLatitude double precision, decimalLongitude double precision, bottomDepthInMeters double precision, eventRemarks text, samplingProtocol text, sampleLocation text, pi_name text, pi_email text, pi_institution text, recordedBy text, sampleType text, other hstore, metadata hstore) ")
psycopg2.extras.register_uuid()
psycopg2.extras.register_hstore(conn)

# test = {"eventID":uuid.uuid1(),
# "eventDate":dt.date(2018,8,13),"prop":{"bottomDepth":"100.3",
# "comment":"This is a test"}}

# cur.execute("Insert INTO test (eventID, eventDate, prop) VALUES (%s, %s,
# %s)",
#           (test["eventID"], test["eventDate"], test["prop"]))


url = "/home/pal/Documents/AeN/Cruise/2018707/SAMPLE LOGS/Corrected/AeN_JC1-2_2018707_Benthos_Lis Lindal Jørgensen.xlsx"


def to_dict(keys, values):
    met = {}
    for r in range(len(keys)):
        if str(values[r]) == 'nan':
            met[keys[r]] = None
        else:
            met[keys[r]] = str(values[r])

    return met


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
    stat = ""
    indxs = []

    for r in REQUIERED:
        indxs.append(np.where(data[0, :] == r)[0][0])
        stat = stat + "%s,"
    o_indxs = find_missing(indxs, data.shape[1])

    stat = stat + "%s,%s"  # For the other and metadata

    for r in range(1, data.shape[0]):
        row = []
        cols = data[r, indxs].tolist()
        cols = replace_nan(cols)
        cols.append(to_dict(data[0, o_indxs], data[r, o_indxs]))
        cols.append(meta)
        if cols[0] == None:
            continue

        print(len(indxs)+2)
        print(stat)
        cur.execute("INSERT INTO aen VALUES("+stat+")",
                    cols)

    #    sheet = workbook.add_worksheet('Metadata')

    #    metadata_fields = ['title', 'abstract', 'pi_name', 'pi_email', 'pi_institution',
    #                       'pi_address', 'recordedBy', 'projectID']


good, error, data, metadata = px.run(url, return_data=True)

if good:
    insert_db(cur, data, metadata)
else:
    print("Errors found")
    for line in error:
        print(line)


conn.commit()
cur.close()
conn.close()

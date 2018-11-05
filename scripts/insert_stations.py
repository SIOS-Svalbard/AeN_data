#! /usr/bin/env python3
import psycopg2
import psycopg2.extras
import uuid
import process_xlsx as px
import datetime as dt
import glob
import pandas as pd
from collections import OrderedDict

conn = psycopg2.connect("dbname=test user=pal")
cur = conn.cursor()


COLUMNS = {"eventID": "uuid",
           "stationName": "text",
           "decimalLatitude": "double precision",
           "decimalLongitude": "double precision",
           "sampleType": "text"}

file_name = "stations.csv"
stations = pd.read_csv(file_name)


def insert_db(cur, data):
    exists_query = '''
    select exists(
        select 1
        from aen
        where eventid= %s
    )'''
    query = '''INSERT INTO aen (eventID, stationName, decimalLatitude, decimalLongitude, sampleType, created, modified, history, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    for index, row in data.iterrows():
        cur.execute(exists_query, (row['eventID'],))
        exists = cur.fetchone()[0]
        if not(exists):
            created = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            cur.execute(query, (row['eventID'], row['stationName'],
                                row['decimalLatitude'], row['decimalLongitude'], row['sampleType'], created, created, created + ": Initial read in of stations", file_name))
        else:
            print("Skipping due to duplicate id " + row['eventID'])
            continue


insert_db(cur, stations)

conn.commit()
cur.close()
conn.close()

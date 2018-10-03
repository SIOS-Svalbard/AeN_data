#!/usr/bin/python3
# encoding: utf-8
'''
 -- Goes though the database and finds children with registered parents without
 an entry


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''

import psycopg2
import sys
from psycopg2 import sql
import psycopg2.extras
import uuid
import config.fields as fields
import numpy as np
import datetime as dt
import glob


__all__ = []
__version__ = 0.1
__date__ = '2018-10-03'
__updated__ = '2018-10-03'


COLUMNS = ["cruiseNumber",
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
           "eventRemarks",
           "metadata"]

def find_missing(cur):
    """
    Goes though database table and finds missing parents

    Parameters
    ----------
    cur: psycopg2 cursor

    """

    cur.execute('''SELECT DISTINCT parenteventid 
            FROM aen
            WHERE parenteventid IS NOT NULL 
            AND 
            parenteventid NOT IN (SELECT DISTINCT eventid FROM aen)''')

    res = cur.fetchall()
    print("Not registered parents:")
    for r in res:
        print(r[0])


def main():
    conn = psycopg2.connect("dbname=test user=pal")
    cur = conn.cursor()
    find_missing(cur)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    sys.exit(main())

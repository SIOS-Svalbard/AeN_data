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
import darwinsheet.config.fields as fields
import numpy as np
import datetime as dt
import glob


__all__ = []
__version__ = 0.1
__date__ = '2018-10-03'
__updated__ = '2019-03-21'


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

    cur.execute('''SELECT distinct parenteventid
            FROM aen
            WHERE parenteventid IS NOT NULL 
            AND 
            parenteventid NOT IN (SELECT DISTINCT eventid FROM aen)
            ORDER BY parenteventid ASC''')

    res = cur.fetchall()
    if res == []:
        return

    print("Not registered parents:")
    print("Parent, One of the children, sample type, source")
    for r in res:
        cur.execute(
            '''SELECT eventid,sampletype,source from aen where parenteventid=%s limit 1''', r)
        c = cur.fetchone()
        print(r[0], c[0], c[1], c[2])


def main():
    conn = psycopg2.connect("dbname=test user=pal")
    cur = conn.cursor()
    find_missing(cur)

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    sys.exit(main())

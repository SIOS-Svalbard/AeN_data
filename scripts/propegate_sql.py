#!/usr/bin/python3
# encoding: utf-8
'''
 -- Goes though the database and propagates inherited fields


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
__date__ = '2018-09-10'
__updated__ = '2018-09-10'


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


def get_children(cur, eventID):
    """
    Returns a list of eventIDS for the children of the input eventID.
    Recursivly finds all the children

    Parameters
    ----------
    cur: psycopg2 cursor

    eventID: string
        The id of the parent    

    Returns
    ----------
    eventIDs: list of strings
        list of all the children
        list is empty if there are no children
    """

    cur.execute(
        "SELECT eventID FROM aen WHERE parenteventid = (%s) ", (eventID,))

    res = cur.fetchall()
    eventIDs = []
    if not res:
        # Empty
        return eventIDs
    else:
        # Not empty
        for r in res:
            cID = str(r[0])
            eventIDs.append(cID)
            children = get_children(cur, cID)
            if children:
                for c in children:
                    eventIDs.append(c)
        return eventIDs


def get_tops(cur):
    """
    Finds all of the entries in the DB without parents

    Parameters

    cur: psycopg2 cursor

    Returns
    ----------
    eventIDs: list of strings
        list of all top entries
        list is empty if there are non
    """

    cur.execute("select * from aen where parenteventid is NULL")
    res = cur.fetchall()
    eventIDs = []
    for r in res:
        eventIDs.append(str(r[0]))

    return eventIDs


def write_fields(cur, parent, children):
    """
    Writes all the inheritable fields of the parent to the children.
    Children can be grandchildren etc.

    Parameters
    ----------
    cur: psycopg2 cursor

    parent: str
        The ID of the parent

    children: list of str
        The IDs of the children

    """

    # Loop over all the possible fields.

    inheritable = ["metadata"]
    for f in fields.fields:
        if f['name'] in COLUMNS:
            if "inherit" in f and f["inherit"]:
                inheritable.append(f['name'])

    query = sql.SQL("SELECT {} from aen where eventid = %s")
    query2 = sql.SQL("UPDATE aen set {} = %s where eventid = %s")
    for col in inheritable:

        cur.execute(query.format((sql.Identifier(col.lower()))), (parent,))
        value = cur.fetchone()[0]
        for child in children:
            cur.execute(
                query2.format((sql.Identifier(col.lower()))), (value, child,))


def inherit(cur):
    """
    Goes though database table and writes all the inherited fields to children,
    grandchildren, .... 

    Parameters
    ----------
    cur: psycopg2 cursor

    """

    tops = get_tops(cur)

    for top in tops:
        children = get_children(cur, top)
        write_fields(cur, top, children)


def main():
    conn = psycopg2.connect("dbname=test user=pal")
    cur = conn.cursor()
    inherit(cur)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    sys.exit(main())

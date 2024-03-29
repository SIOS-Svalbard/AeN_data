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
import darwinsheet.config.fields as fields
import numpy as np
import datetime as dt
import glob
import getpass


__all__ = []
__version__ = 0.2
__date__ = '2018-09-10'
__updated__ = '2019-03-22'


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
           "metadata",
           "cruiseName"]


def get_children(cur, eventID):
    """
    Returns a list of eventIDS for the children of the input eventID.

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
            #children = get_children(cur, cID)
            # if children:
            # for c in children:
            # eventIDs.append(c)
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


def write_fields(cur, parent, children, inheritable, weak):
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

    inheritable: list of str
        The fields that can be inherited to children

    weak: list of str
        The fields that can be only be inherited to children if field is empty
        Should also be in inheritable 
    """

    query = sql.SQL("SELECT {} from aen where eventid = %s")
    query2 = sql.SQL("UPDATE aen set {} = %s where eventid = %s")
    query3 = sql.SQL("UPDATE aen set other = other || %s where eventid = %s")
    for col in inheritable:
        if col in COLUMNS:  # We are working with a name in the columns
            cur.execute(query.format((sql.Identifier(col.lower()))), (parent,))
            value = cur.fetchone()[0]
            if value != None:  # Make sure we are not removing information
                for child in children:
                    if col in weak:  # Only inherit if empty
                        cur.execute(query.format(
                            (sql.Identifier(col.lower()))), (child,))
                        c_value = cur.fetchone()[0]
                        if c_value != None:  # Something there, so we continue
                            continue
                    cur.execute(
                        query2.format((sql.Identifier(col.lower()))), (value, child,))
        else:  # We are working with a name that could be in other
            # Get contents of other
            cur.execute(query.format((sql.Identifier('other'))), (parent,))
            other = cur.fetchone()[0]
            if other and col in other.keys() and other[col] != '':
                value = {col: other[col]}
                for child in children:
                    cur.execute(query.format(
                        (sql.Identifier('other'))), (child,))
                    c_other = cur.fetchone()[0]
                    if c_other and col in c_other.keys() and c_other[col] != '':
                        continue  # Something there, so we continue

                    cur.execute(query3, (value, child,))


def inherit(cur):
    """
    Goes though database table and writes all the inherited fields to children,
    grandchildren, .... 

    Parameters
    ----------
    cur: psycopg2 cursor

    """

    tops = get_tops(cur)

    # Loop over all the possible fields.
    inheritable = []  # ["metadata"]
    weak = []  # For holding weak inheritance
    for f in fields.fields:
        if "inherit" in f and f["inherit"]:
            inheritable.append(f['name'])
            if "inherit_weak" in f and f["inherit_weak"]:
                weak.append(f['name'])

    traverse_three(cur, tops, inheritable, weak)


def traverse_three(cur, tops, inheritable, weak):
    '''
    Recursive function for moving though all the parents and their children, 
    grandchildren ...

    Parameters
    ----------

    cur: psycopg2 cursor

    tops: list of str
        The parentEventIDs (parents) 

    inheritable: list of str
        The fields that can be inherited to children

    weak: list of str
        The fields that can be only be inherited to children if field is empty
        Should also be in inheritable 
    '''
    for top in tops:
        children = get_children(cur, top)
        if children != []:
            write_fields(cur, top, children, inheritable, weak)
            traverse_three(cur, children, inheritable,
                           weak)  # Take next level down


def main():
    # Connect to the database as the user running the script
    conn = psycopg2.connect('dbname=aen_db user=' + getpass.getuser())
    psycopg2.extras.register_hstore(conn)  # Make sure that hstore goes to dict
    cur = conn.cursor()
    inherit(cur)

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    sys.exit(main())

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


__all__ = []
__version__ = 0.1
__date__ = '2018-09-25'
__updated__ = '2018-09-25'


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
# Dict with old (key) and new (value) to replace

rep = {"P1": "P1 (NLEG01)",
       "P2": "P2 (NLEG04)",
       "P3": "P3 (NLEG07)",
       "NLEG-P3": "P3 (NLEG07)",
       "P4": "P4 (NLEG11)",
       "P5": "P5 (NLEG13)",
       "P6": "P6 (NLEG21)",
       "P7": "P7 (NLEG25)",
       "PICE": "PICE1",
       "Pice1": "PICE1",
       "PICE1 ": "PICE1",
       "Sice1": "SICE1",
       "SICE 1": "SICE1",
       "R1": "Raphaelle 1",
       "Sice2b": "SICE2b",
       "SICE2": "SICE2a",
       "Sice3": "SICE3"}


def replace(cur, field, old, new):
    """
    Find and replace on a field in the database. 

    Parameters
    ----------
    cur: psycopg2 cursor

    field: str
        The field in which the string is located

    old: The old value to be found

    new: the new value to replace the old

    """

    query = sql.SQL("UPDATE aen SET {0} = %s where {0} LIKE %s")
    cur.execute(query.format(
        (sql.Identifier(field))), (new, old))


def main():
    conn = psycopg2.connect("dbname=test user=pal")
    cur = conn.cursor()
    for key, value in rep.items():
        replace(cur, "stationname", key, value)
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    sys.exit(main())

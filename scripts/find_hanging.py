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
import psycopg2.extras
import getpass


__all__ = []
__version__ = 0.2
__date__ = '2018-10-03'
__updated__ = '2021-05-25'


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
    print("Parent, One of the children, sample type, cruise number, source")
    for r in res:
        cur.execute(
            '''SELECT eventid,sampletype,cruisenumber,source from aen where parenteventid=%s limit 1''', r)
        c = cur.fetchone()
        print(f'{r[0]}, {c[0]}, {c[1]}, {c[2]}, {c[3]}')


def main():
    # Connect to the database as the user running the script
    conn = psycopg2.connect('dbname=aen_db user=' + getpass.getuser())
    cur = conn.cursor()
    find_missing(cur)

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    sys.exit(main())

#! /usr/bin/env python3
# encoding: utf-8
'''
 -- Initialises the database


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''

__all__ = []
__version__ = 0.1
__date__ = '2019-03-22'
__updated__ = '2019-03-22'

import psycopg2
import psycopg2.extras
import getpass

exe_str = '''
CREATE TABLE aen (eventID uuid PRIMARY KEY,
                              parentEventID uuid,
                              cruiseNumber int,
                              cruiseName text,
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
                              metadata hstore,
                              created timestamp with time zone,
                              modified timestamp with time zone,
                              history text,
                              source text) '''


# Connect to the database as the user running the script
conn = psycopg2.connect('dbname=aen_db user=' + getpass.getuser())
cur = conn.cursor()
cur.execute("CREATE EXTENSION IF NOT EXISTS hstore;")
cur.execute(exe_str)
cur.execute("GRANT ALL privileges ON TABLE public.aen TO aen_user;")
conn.commit()
cur.close()
conn.close()

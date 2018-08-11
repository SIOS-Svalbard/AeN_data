#!/usr/bin/python3
# encoding: utf-8
'''
 -- Writes a uuid.txt file with 1000 uuids


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''
import uuid_labels as uu

f = open("uuid.txt","w")
for i in range(1000):
    f.write(uu.new_hex_uuid()+"\n")
f.close()

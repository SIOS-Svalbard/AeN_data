#!/usr/bin/python3
# encoding: utf-8
'''
 -- Writes a uuid.txt file with 1000 uuids


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''
import uuid
f = open("uuid.txt", "w")
for i in range(2000):
    f.write(str(uuid.uuid1())+"\n")
f.close()

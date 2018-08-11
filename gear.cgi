#!/usr/bin/python3
# encoding: utf-8


'''
 -- Web interface for making PDF with UUIDs


@author:     Pål Ellingsen
@deffield    updated: Updated
'''


import os
import sys
import cgi
import cgitb
import uuid
import datetime as dt
import socket 
import AeN.scripts.uuid_labels as uu
import tempfile
import shutil

__updated__ = '2018-08-09'


cgitb.enable()


method = os.environ.get("REQUEST_METHOD", "GET")

from mako.template import Template
from mako.lookup import TemplateLookup

templates = TemplateLookup(
    directories=['templates'], output_encoding='utf-8')


# Using sys, as print doesn't work for cgi in python3
template = templates.get_template("gear.html")


def warn(message):
    message = bytes(message,"utf-8")
    sys.stdout.buffer.write(b'<p style="color:red">'+message+b'</p>')
# method = "POST"
if method =="GET":
    sys.stdout.flush()
    sys.stdout.buffer.write(b"Content-Type: text/html\n\n")

    sys.stdout.buffer.write(template.render())

elif method == "POST":
    
    form = cgi.FieldStorage()

    def get_value(field,integer=False):
        if field in form:
            return form[field].value
        elif integer:
            return 0
        else:
            return ''
    gear = get_value('gear')
    sample = get_value('sample')
    m = int(get_value('m',True))
    n = int(get_value('n',True))

    fd, path = tempfile.mkstemp()
    uu.save_pages(path, gearText=gear,sampleText=sample,M=m, N=n )

    print("Content-Type: application/pdf\n")
    print('Content-Disposition: attachment; filename="'+gear+'.pdf"\n')
    try:
        with open(path, "rb") as f:
            sys.stdout.flush()
            shutil.copyfileobj(f, sys.stdout.buffer)
            
    finally: 
        os.remove(path)
    sys.stdout.flush()


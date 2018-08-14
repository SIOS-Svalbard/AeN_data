#!/usr/bin/python3
# encoding: utf-8


'''
 -- Web interface for printing labels


@author:     Pål Ellingsen
@deffield    updated: Updated
'''


import os
import io
import sys
import cgi
import cgitb
import AeN.scripts.process_xlsx as px
__updated__ = '2018-08-13'


cgitb.enable()

method = os.environ.get("REQUEST_METHOD", "GET")

from mako.template import Template
from mako.lookup import TemplateLookup

templates = TemplateLookup(
    directories=['templates'], output_encoding='utf-8')


# method = 'POST'
# method = 'Test'

#if method == "GET":  # This is for getting the page


# Using sys, as print doesn't work for cgi in python3
template = templates.get_template("check.html")

sys.stdout.flush()
sys.stdout.buffer.write(b"Content-Type: text/html\n\n")

def write_page():
    # Write the page
    sys.stdout.buffer.write(
        template.render())


def warn(message):
    message = bytes(message,"utf-8")
    sys.stdout.buffer.write(b'<p style="color:red">'+message+b'</p>')

if method == "POST":
    
    sys.stdout.buffer.write(b"<!doctype html>\n<html>\n <meta charset='utf-8'>")
    form = cgi.FieldStorage()
    warn(form['myfile'].filename)
    # print(form['myfile'].value)
    # warn(form)
    good, error = px.run(io.BytesIO(form['myfile'].value))
    if good:
        warn("File OK :)")
    else:
        warn("File is not ok :(")
        warn("The following errors were found:")
    for line in error:
        warn(line)
        
    sys.stdout.buffer.write(b'</html>')
elif method == "GET":
    write_page()

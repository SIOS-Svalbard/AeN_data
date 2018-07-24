#!/usr/bin/python3
# encoding: utf-8


'''
 -- Web interface for generating an UUID.


@author:     Pål Ellingsen
@deffield    updated: Updated
'''


import os
import time
import sys
import cgi
import cgitb
import codecs
import uuid
import shutil
import textwrap

__updated__ = '2018-06-29'


# cgitb.enable()


method = os.environ.get("REQUEST_METHOD", "GET")

from mako.template import Template
from mako.lookup import TemplateLookup

templates = TemplateLookup(
    directories=['templates'], output_encoding='utf-8')


# method = 'POST'
# method = 'Test'

if method == "GET":  # This is for getting the page

    # Using sys, as print doesn't work for cgi in python3
    template = templates.get_template("uuid.html")

    sys.stdout.flush()
    sys.stdout.buffer.write(b"Content-Type: text/html\n\n")
    sys.stdout.buffer.write(
        template.render(uuid=uuid))

elif method == "POST":
    template = templates.get_template("uuid.html")

    sys.stdout.flush()
    sys.stdout.buffer.write(b"Content-Type: text/html\n\n")
    sys.stdout.buffer.write(
        template.render(uuid=uuid))

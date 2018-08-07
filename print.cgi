#!/usr/bin/python3
# encoding: utf-8


'''
 -- Web interface for printing labels


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

__updated__ = '2018-07-25'


cgitb.enable()








method = os.environ.get("REQUEST_METHOD", "GET")

from mako.template import Template
from mako.lookup import TemplateLookup

templates = TemplateLookup(
    directories=['templates'], output_encoding='utf-8')

def create_label(uuid, text1, text2, text3, text4):
    """
    Creates the ZPL code for the label.
    Adds a text with the 8 first chracters from the uuid for ease of reading

    Parameters
    ----------
    uuid : str
        The 32 characters hex uuid

    text1 : str
        First line of text, limited to 18 characters

    text2 : str
        Second line of text, limited to 18 characters

    text3 : str
        Third line of text, limited to 18 characters

    text4 : str
        Fourth line of text, limited to 18 characters    

    Returns
    ----------
    zpl : str
        The formatted ZPL code string that should be sent to the Zebra printer 
    """

    # This uses a template made with ZebraDesigner, replacing the variables
    # with the necessary text {X}.
    zpl = '''
CT~~CD,~CC^~CT~
^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR4,4~SD30^JUS^LRN^CI28^XZ
^XA
^MMT
^PW898
^LL0295
^LS0
^BY110,110^FT506,141^BXN,4,200,22,22,1,~
^FH\^FD{0}^FS
^FT463,181^A0N,21,21^FH\^FD{1}^FS
^FT463,214^A0N,21,21^FH\^FD{2}^FS
^FT462,247^A0N,21,21^FH\^FD{3}^FS
^FT463,283^A0N,21,21^FH\^FD{4}^FS
^FT462,33^A0R,21,21^FH\^FD{5}^FS
^PQ1,0,1,Y^XZ'''.format(uuid, 
        text1, 
        text2,
        text3,
        text4,
        # text1.encode(encoding='utf-8'), 
        # text2.encode(encoding='utf-8'),
        # text3.encode(encoding='utf-8'),
        # text4.encode(encoding='utf-8'),
        uuid[:8])

#    print(zpl)
    return zpl


# method = 'POST'
# method = 'Test'

#if method == "GET":  # This is for getting the page


# Using sys, as print doesn't work for cgi in python3
template = templates.get_template("print.html")

sys.stdout.flush()
sys.stdout.buffer.write(b"Content-Type: text/html\n\n")
sys.stdout.buffer.write(
    template.render(today=str(dt.date.today())))

if method == "POST":
    
    form = cgi.FieldStorage()
    # Check if the label is generated now and not a refresh
    # sys.stdout.buffer.write(bytes(str(dt.datetime.now().timestamp()-5)+"<br>","utf-8"))
    if float(form['print'].value)<dt.datetime.now().timestamp()-5:
        sys.stdout.buffer.write(b"Not printing. Was this a refresh?")
        sys.exit()
    # sys.stdout.buffer.write(bytes(form["print"].value+"<br>",'utf-8')) 
    PORT = 9100
    BUFFER_SIZE = 1024
    try: 
        pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pSocket.connect((form['ip'].value, PORT))
    except (ConnectionRefusedError,OSError):
        sys.stdout.buffer.write(b"Error, wrong IP")
        sys.exit() 
    def get_value(field):
        if field in form:
            return form[field].value
        else:
            return ''
    text1 = get_value('text1')
    text2 = get_value('text2')
    text3 = get_value('text3')
    text4 = get_value('text4')

    for n in range (int(form['n'].value)):
        zpl = create_label(str(uuid.uuid1()),text1, text2, text3, text4)
        pSocket.send(bytes(zpl,"utf-8"))
        sys.stdout.buffer.write(bytes("Label printed<br>","utf-8")) 
        # sys.stdout.buffer.write(bytes(zpl,"utf-8"))

    pSocket.close()


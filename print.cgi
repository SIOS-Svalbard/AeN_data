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

SETUP_DEFAULT = "L"

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
^BY110,110^FT506,111^BXN,4,200,22,22,1,~
^FH\^FD{0}^FS
^FT445,151^A0N,21,21^FH\^FD{1}^FS
^FT445,184^A0N,21,21^FH\^FD{2}^FS
^FT445,217^A0N,21,21^FH\^FD{3}^FS
^FT445,253^A0N,21,21^FH\^FD{4}^FS
^FT462,33^A0R,21,21^FH\^FD{5}^FS
^PQ1,0,1,Y^XZ'''.format(uuid, 
        text1, 
        text2,
        text3,
        text4,
        uuid[:8])

#    print(zpl)
    return zpl

def create_large(uuid, text1, text2, text3, text4,text5):
    """
    Creates the ZPL code for the large (25x51 mm) label.
    Adds a text with the 8 first characters from the uuid for ease of reading

    Parameters
    ----------
    uuid : str
        The 32 characters hex uuid

    text1 : str
        First line of text, limited to 20 characters

    text2 : str
        Second line of text, limited to 20 characters

    text3 : str
        Third line of text, limited to 20 characters

    text4 : str
        Fourth line of text, limited to 26 characters    

    text5 : str
        Fifth line of text, limited to 26 characters    

    Returns
    ----------
    zpl : str
        The formatted ZPL code string that should be sent to the Zebra printer 
    """

    zpl= '''
CT~~CD,~CC^~CT~
^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR4,4~SD25^JUS^LRN^CI28^XZ
^XA
^MMT
^PW602
^LL0295
^LS0
^BY110,110^FT465,143^BXN,5,200,22,22,1,~
^FH\^FD{0}^FS
^FT491,171^A0N,21,21^FH\^FD{6}^FS
^FT20,57^A0N,42,40^FH\^FD{1}^FS
^FT20,109^A0N,42,40^FH\^FD{2}^FS
^FT20,161^A0N,42,40^FH\^FD{3}^FS
^FT20,216^A0N,42,40^FH\^FD{4}^FS
^FT20,268^A0N,42,40^FH\^FD{5}^FS
^PQ1,0,1,Y^XZ'''.format(uuid,
        text1, 
        text2,
        text3,
        text4,
        text5,
        uuid[:8])

    return zpl



form = cgi.FieldStorage()

if 'setup' in form:
    setup = form['setup'].value
else:
    setup = SETUP_DEFAULT

# Using sys, as print doesn't work for cgi in python3
if setup == 'L':
    template = templates.get_template("print_large.html")
elif setup =='M':
    template = templates.get_template("print_medium.html")

sys.stdout.flush()
sys.stdout.buffer.write(b"Content-Type: text/html\n\n")

texts = {"text1":str(dt.date.today())+" AeN","text2":"","text3":"","text4":"","text5":""}
incr = False

def write_page(texts,incr):
    # Write the page
    sys.stdout.buffer.write(
        template.render(today=str(dt.date.today()),texts=texts,incr=incr))


def warn(message):
    message = bytes(message,"utf-8")
    sys.stdout.buffer.write(b'<p style="color:red">'+message+b'</p>')

if method == "POST":
    
    # Check if the label is generated now and not a refresh
    # sys.stdout.buffer.write(bytes(str(dt.datetime.now().timestamp()-5)+"<br>","utf-8"))
    # if float(form['print'].value)<dt.datetime.now().timestamp()-75:
    #     warn("Not printing. Was this a refresh? If not your computer might be out of sync with the time server (limit 75s)<br> Difference to server in seconds:" +str(float(form['print'].value)-dt.datetime.now().timestamp()))
    #     write_page(texts,incr)
    #     sys.exit()
    # sys.stdout.buffer.write(bytes(form["print"].value+"<br>",'utf-8')) 
    PORT = 9100
    BUFFER_SIZE = 1024
    try: 
        pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pSocket.connect((form['ip'].value, PORT))
    except (ConnectionRefusedError,OSError):
        warn("Error, wrong IP")
        write_page(texts,incr)
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
    text5 = get_value('text5')
    if "increment" in form:
        incr = form['increment'].value=="y"
    else:
        incr = False

    org_text3=text3
    if incr:
        try:
            n_zero = str(len(text3))
            text3 = int(text3)
        except ValueError:
            warn('Text3 is not a number and increment is ticked.')
            write_page(texts,incr)
            sys.exit()
    for n in range(int(form['n'].value)):
        if incr:
            if setup == 'L':
                zpl = create_large(str(uuid.uuid1()),text1, text2, format(text3,"0"+n_zero+"d"), text4,text5)
            elif setup=='M':
                zpl = create_label(str(uuid.uuid1()),text1, text2, format(text3,"0"+n_zero+"d"), text4)
        else:
            if setup == 'L':
                zpl = create_large(str(uuid.uuid1()),text1, text2, text3, text4,text5)
            elif setup =='M':
                zpl = create_label(str(uuid.uuid1()),text1, text2, text3, text4)
                
        pSocket.send(bytes(zpl,"utf-8"))
        #warn("Down for maintainance")
        #sys.stdout.buffer.write(bytes(zpl,"utf-8"))
        if incr:
            text3=text3+1

    warn("Label printed<br>") 
    if incr:
        texts = {
            "text1":text1,
            "text2":text2,
            "text3":format(text3,"0"+n_zero+"d"),
            "text4":text4,
            "text5":text5}
    else:
        texts = {
            "text1":text1,
            "text2":text2,
            "text3":text3,
            "text4":text4,
            "text5":text5}
    pSocket.close()

write_page(texts,incr)

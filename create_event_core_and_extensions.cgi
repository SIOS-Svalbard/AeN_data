#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 13:54:02 2021

Web interface for a tool to retrieve metadata from the metadata catalogue
and insert into a provided data sheet that includes an eventID column

@author: Luke Marsden
"""
import os
import sys
import cgi
import cgitb
import numpy as np
import pandas as pd
import shutil
import http.cookies as Cookie
import tempfile
from openpyxl import load_workbook
metadata_retrieval_filepath = 'scripts'
sys.path.insert(0, metadata_retrieval_filepath)
from create_event_core_and_extensions import run as create_event_core_and_extensions
from mako.lookup import TemplateLookup

def print_html_template():
    '''
    Prints the html template. Excluding closing the <main> element which must be closed at the bottom of this script
    '''
    template = templates.get_template("create_event_core_and_extensions.html")
    sys.stdout.flush()
    sys.stdout.buffer.write(b"Content-Type: text/html\n\n")
    sys.stdout.buffer.write(template.render())

def validate_form(form, tmpfile):
    '''
    Validations for the information entered

    Parameters
    ----------
    form : cgi.Fieldstorage()
        Information provided by the user

    tmpfile : string
    	Filepath showing temporary location of file uploaded by user

    Returns
    -------
    good : boolean
        If TRUE, all validations passed and can proceed with script, otherwise, it must be terminated.
    errors : string
    	Error text
    sheet_name: string
    	Name of excel sheet containing data with eventID column
    header_row_number: integer
    	Number of row that contains column headers
    data_first_row_number: integer
    	Number of first row that includes data
    '''
    errors = []
    good = True

    filetype = form["myfile"].filename.split('.')[-1]

    if "header_row_number" in form and "data_first_row_number" in form:

    	try:
    		header_row_number = int(form["header_row_number"].value)
    	except:
    		errors.append("Please enter the row number that contains the column headers. This must be an integer.")
    		header_row_number = np.nan
    		good = False
    	try:
    		data_first_row_number = int(form["data_first_row_number"].value)
    	except:
    		data_first_row_number = np.nan
    		errors.append("Please enter the number of the first row that includes data. This must be an integer.")
    		good = False

    	if data_first_row_number <= header_row_number:
    		good = False
    		errors.append("The number for the first row including data should be greater than the header row")

    	if header_row_number < 1:
    		good = False
    		errors.append("The row number that includes headers must be greater than or equal to 1, where 1 is the first line (not 0).")

    	if filetype in ['xlsx','xls']:
    		if "sheet_name" in form:
    			sheet_name = form["sheet_name"].value
    			if filetype == 'xlsx':
    				wb = load_workbook(tmpfile, read_only=True)
    				if sheet_name not in wb.sheetnames:
			    		good = False
			    		if sheet_name == '':
			    			errors.append('You have uploaded a spreadsheet file. Please enter a sheet name.')
			    		else:
			    			errors.append(f'Sheet name "{sheet_name}" not found in the file "{form["myfile"].filename}".')
    			elif filetype == 'xls':
    				xls = pd.read_excel(tmpfile, sheet_name = None)
    				if sheet_name not in xls.keys():
    					good = False
			    		if sheet_name == '':
			    			errors.append('You have uploaded a spreadsheet file. Please enter a sheet name.')
			    		else:
			    			errors.append(f'Sheet name "{sheet_name}" not found in the file "{form["myfile"].filename}".')

    		else:
    			errors.append("Please enter the name of the sheet that contains your data.")
    			good = False
    	elif filetype in ['csv','tsv']:
    		sheet_name = False
    	elif filetype == '':
    		good = False
    		sheet_name = False
    		errors.append(f"Please select a suitable xls, xlsx, csv or tsv file.")
    	else:
    		good = False
    		sheet_name = False
    		errors.append(f"I have not been programmed to read {filetype} files. Please upload an xls, xlsx, csv or tsv file.")

    else:

    	if "header_row_number" not in form:
    		errors.append("Please enter the row number that contains the column headers.")
    		good = False
    	if "data_first_row_number" not in form:
    		errors.append("Please enter the number of the first row that includes data.")
    		good = False

    return good, errors, sheet_name, header_row_number, data_first_row_number

def warn(message,color='red'):
    message = bytes(message,"utf-8")
    sys.stdout.buffer.write(b'<p style="color:'+bytes(color,"utf-8")+b'">'+message+b'</p>')

cgitb.enable() # comment out when not developing tool

cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

method = os.environ.get("REQUEST_METHOD", "GET")

templates = TemplateLookup(directories = ['templates'], output_encoding='utf-8')

if method == "GET": # This is for getting the page
    print_html_template()

if method == "POST":

    form = cgi.FieldStorage()

    filetype = form["myfile"].filename.split('.')[-1]
    tmpfile = '/tmp/tmpfile.'+filetype
    with open(tmpfile, 'wb') as f:
    	f.write(form["myfile"].file.read())

    good, errors, sheet_name, header, data_first_row_number = validate_form(form, tmpfile)

    if good:

    	outputFileName = 'event_core_and_extensions.xlsx'
    	print("Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    	print("Content-Disposition: attachment; filename="+outputFileName+"\n")
    	path = "/tmp/" + next(tempfile._get_candidate_names()) + '.xlsx'


    	create_event_core_and_extensions(tmpfile,sheet_name,header,data_first_row_number,path)

    	with open(path, "rb") as f:
    		sys.stdout.flush()
    		shutil.copyfileobj(f, sys.stdout.buffer)

    if not good:
    	sys.stdout.flush()
    	sys.stdout.buffer.write(b"Content-Type: text/html\n\n")
    	sys.stdout.buffer.write(b"<!doctype html>\n<html>\n <meta charset='utf-8'>")
    	warn(form['myfile'].filename,color='black')
    	warn("The following errors were found:")
    	for error in errors:
    		warn(error)
    	sys.stdout.buffer.write(b'</html>')

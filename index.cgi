#!/usr/bin/python3
# encoding: utf-8


'''
 -- Web interface for generating Excel sheet.
 Fork of https://github.com/umeldt/darwinsheet


@author:     Pål Ellingsen
@author:     Christian Svindseth
@deffield    updated: Updated
'''


import os
import sys
import cgi
import cgitb
import codecs
import uuid
import yaml
import rdflib
import tempfile
import xlsxwriter
import shutil
import http.cookies as Cookie
import textwrap

__updated__ = '2018-06-21'


# cgitb.enable()


cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))


class Term:
    terms = []

    @staticmethod
    def get(id):
        for t in Term.terms:
            if t.uri == id or t.name == id:
                return t
        return Term(id)

    def __init__(self, uri):
        self.uri = uri
        self.name = uri.rsplit("/", 1)[-1]
        self.labels = {}
        self.examples = {}
        self.definitions = {}
        self.validations = {}
        Term.terms.append(self)

    def translate(self, d, lang):
        if lang in d:
            return d[lang]
        if '_' in d:
            return d['_']
        return ""

    def label(self, lang=None):
        return self.translate(self.labels, lang)

    def example(self, lang=None):
        return self.translate(self.examples, lang)

    def definition(self, lang=None):
        return self.translate(self.definitions, lang)

    def validation(self, lang=None):
        return self.translate(self.validations, lang)


config = yaml.load(
    open(os.path.join("config", "config.yaml"), encoding='utf-8'))['cores'][0]['sheets'][0]
# Put the language in an ordered place
config['languages'] = yaml.load(
    open(os.path.join("config", "config.yaml"), encoding='utf-8'))['languages']


g = rdflib.Graph()
g.load("dwcterms.rdf")
# Populate the terms with the terms from dwc
for s, p, o in g:
    term = Term.get(s)
    if str(p) == "http://www.w3.org/2000/01/rdf-schema#comment":
        term.examples["_"] = str(o)
    elif str(p) == "http://purl.org/dc/terms/description":
        term.definitions["_"] = str(o)

# Translate terms
t = rdflib.Graph()
t.load("dwctranslations.rdf")
for s, p, o in t:
    if type(o) == rdflib.term.Literal and o.language:
        term = Term.get(s)
        if str(p) == "http://www.w3.org/2004/02/skos/core#example":
            term.examples[o.language] = str(o)
        elif str(p) == "http://www.w3.org/2004/02/skos/core#definition":
            term.definitions[o.language] = str(o)
        elif str(p) == "http://www.w3.org/2004/02/skos/core#prefLabel":
            term.labels[o.language] = str(o)

# Add terms not in dwc
try:
    import AeN.scripts.config.fields as fields
    for field in fields.fields:
        term = Term.get(field['name'])

        if not(term.labels):  # Set the label
            term.labels = {'en': field['disp_name']}

        if not(term.validations):  # Set the validation input

            term.validations = {'en': field['valid']['input_message']}


except ImportError as e:
    # Module fields not found
    pass

ignore = []  # ["Organism", "Occurrence", "Taxon"]  # ?

mofterms = [
    "measurementID", "measurementType", "measurementValue",
    "measurementAccuracy", "measurementUnit",
    "measurementDeterminedBy", "measurementDeterminedDate",
    "measurementMethod"
]

# Is this used?
dwcterms = [t for t in Term.terms if t.name not in ignore]

method = os.environ.get("REQUEST_METHOD", "GET")

from mako.template import Template
from mako.lookup import TemplateLookup

templates = TemplateLookup(
    directories=['templates'], output_encoding='utf-8')

if 'language' in cookie:
    language = cookie['language'].value
else:
    language = 'en'

# method = 'POST'

if method == "GET":  # This is for getting the page

    # Using sys, as print doesn't work for cgi in python3
    template = templates.get_template("index.html")

    sys.stdout.flush()
    sys.stdout.buffer.write(b"Content-Type: text/html\n\n")
    sys.stdout.buffer.write(
        template.render(config=config, Term=Term, lang=language))

elif method == "POST":
    form = cgi.FieldStorage()
    if 'language' in form:
        cookie['language'] = form['language'].value
        print(cookie.output())
        print("Status: 303 See other")
        print("Location: %s\n" % os.environ["HTTP_REFERER"])
        sys.exit(0)

    reserved = []  # ['measurementorfact', 'uuid']
#     form = ['uuid', 'shipid', 'eventDate',
#             'decimalLatitude', 'decimalLongitude']
    terms = []

    # Build list of terms from config, this is for sorting
    terms_config = []
#     print(config['terms'])
    for group in config['grouping']:
        #         print(group)
        for term in config['terms'][group]:
            terms_config.append(term)
#     print(terms_config)
#     print(terms)
    # Use the config terms to sort the terms from the form
    for term in terms_config:
        if term in form and term not in reserved:
            terms.append(term)

    print("Content-Type: application/vnd.ms-excel")
    print("Content-Disposition: attachment; filename=template.xlsx\n")

#     for term in Term.terms:
#         print(term.name, term.definitions)
#     print(terms)

    path = "/tmp/" + next(tempfile._get_candidate_names()) + '.xlsx'

    import AeN.scripts.make_xlsx as mx

    # Need to make the field_dict and append usefull info from dwc
    field_dict = mx.make_dict_of_fields()
    depth = field_dict['eventDate']
#     print(depth.name, depth.disp_name, depth.validation)
#     print(terms)

    for t in Term.terms:
        #         print(field)
        if t.name in field_dict.keys():
            if t.definition(language):
                #                 print(t.name)
                valid = field_dict[t.name].validation

                valid['input_message'] = valid['input_message'] + \
                    '\n\nDarwin core supl. info:\n' + \
                    textwrap.fill(
                        ' '.join(t.definition(language).split()), width=40)
                field_dict[t.name].set_validation(valid)
    depth = field_dict['eventDate']
#     print(depth.name, depth.disp_name, depth.validation)
    mx.write_file(path, terms, field_dict)
#     workbook = xlsxwriter.Workbook(path)
#     occurrences = workbook.add_worksheet("Occurrences")
#
#     overflow = workbook.add_format({'align': 'vjustify'})
#     reqfmt = workbook.add_format({'bold': True, 'bg_color': '#aaffaa'})
#     recfmt = workbook.add_format({'bold': True, 'bg_color': '#ffffaa'})
#     reqfmt.set_shrink()
#
#     for n, name in enumerate(terms):
#         term = Term.get(name)
#         occurrences.write(
#             0, n, term.name, reqfmt if term.name in config['required'] else recfmt)
#         occurrences.write_comment(0, n,
#                                   ("REQUIRED" if term.name in config[
#                                    'required'] else "RECOMMENDED")
#                                   + "\n\n"
#                                   + ' '.join(term.definition(language).split())
#                                   + "\n\n"
#                                   + ' '.join(term.example(language).split()))
#         width = len(term.name) + 6
#         occurrences.set_column(0, n, width)
#
#         if (term.name == 'basisOfRecord'):
#             occurrences.data_validation(1, n, 1000000, n, {
#                 'validate': 'list',
#                 'source': [
#                     'PreservedSpecimen',
#                     'HumanObservation',
#                     'FossilSpecimen',
#                     'LivingSpecimen',
#                     'HumanObservation',
#                     'MachineObservation'
#                 ]
#             })
#
#         if(uuid in form and term == 'occurrenceID'):
#             for row in range(1, 5000):
#                 occurrences.write(row, n,
#                                   "urn:uuid:" + str(uuid.uuid4()), overflow)
#     if 'measurementorfact' in form:
#         mof = workbook.add_worksheet("MeasurementOrFact")
#         for n, name in enumerate(mofterms):
#             term = Term.get(name)
#             mof.write(
#                 0, n, term.name, reqfmt if term.name in config['required'] else recfmt)
#             if term.example(language) and term.definition(language):
#                 mof.write_comment(0, n,
#                                   ("REQUIRED" if term.name in config[
#                                    'required'] else "RECOMMENDED")
#                                   + "\n\n"
#                                   + term.definition(language) + "\n\n" + term.example(language))
#             width = len(term.name) + 6
#             mof.set_column(0, n, width)
#     workbook.close()
    with open(path, "rb") as f:
        sys.stdout.flush()
        shutil.copyfileobj(f, sys.stdout.buffer)

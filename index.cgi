#!/usr/bin/python
# encoding: utf-8

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
import Cookie

reload(sys)
sys.setdefaultencoding('utf-8')

cgitb.enable()

cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

class Term:
    terms = []

    @staticmethod
    def get(id):
        for t in Term.terms:
            if t.uri == id or t.name == id: return t
        return Term(id)

    def __init__(self, uri):
        self.uri = uri
        self.name = uri.rsplit("/", 1)[-1]
        self.labels = {}
        self.examples = {}
        self.definitions = {}
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

g = rdflib.Graph()
g.load("dwcterms.rdf")

config = yaml.load(open("config.yaml"))['cores'][1]['sheets'][0]
config['languages'] = {
    'en': 'English',
    'es': 'Español',
    'ja': '日本語'
}
for s, p, o in g:
    term = Term.get(s)
    if unicode(p) == "http://www.w3.org/2000/01/rdf-schema#comment":
        term.examples["_"] = unicode(o)
    elif unicode(p) == "http://purl.org/dc/terms/description":
        term.definitions["_"] = unicode(o)

t = rdflib.Graph()
t.load("dwctranslations.rdf")
for s, p, o in t:
    if type(o) == rdflib.term.Literal and o.language:
        term = Term.get(s)
        if str(p) == "http://www.w3.org/2004/02/skos/core#example":
            term.examples[o.language] = unicode(o)
        elif str(p) == "http://www.w3.org/2004/02/skos/core#definition":
            term.definitions[o.language] = unicode(o)
        elif str(p) == "http://www.w3.org/2004/02/skos/core#prefLabel":
            term.labels[o.language] = unicode(o)

ignore = [ "Organism", "Occurrence", "Taxon" ]
mofterms = [
        "measurementID", "measurementType", "measurementValue",
        "measurementAccuracy", "measurementUnit",
        "measurementDeterminedBy", "measurementDeterminedDate",
        "measurementMethod"
        ]
dwcterms = [t for t in Term.terms if t.name not in ignore]

method = os.environ.get("REQUEST_METHOD", "GET")

from mako.template import Template
from mako.lookup import TemplateLookup

templates = TemplateLookup(directories=['templates'], output_encoding='utf-8')

if 'language' in cookie:
    language = cookie['language'].value
else:
    language = 'en'

if method == "GET":
    print("Content-Type: text/html\n")
    template = templates.get_template("index.html")
    print(template.render(config = config, Term = Term, lang = language))
elif method == "POST":
    form = cgi.FieldStorage()

    if 'language' in form:
        cookie['language'] = form['language'].value
        print(cookie.output())
        print("Status: 303 See other")
        print("Location: %s\n" % os.environ["HTTP_REFERER"])
        sys.exit(0)

    reserved = ['measurementorfact', 'uuid']
    terms = []
    for term in form:
        if term not in reserved:
            terms.append(term)

    print("Content-Type: application/vnd.ms-excel")
    print("Content-Disposition: attachment; filename=template.xlsx\n")
    path = "tmp/" + next(tempfile._get_candidate_names())
    workbook = xlsxwriter.Workbook(path)
    occurrences = workbook.add_worksheet("Occurrences")

    overflow = workbook.add_format({ 'align': 'vjustify' })
    reqfmt = workbook.add_format({ 'bold': True, 'bg_color': '#aaffaa' })
    recfmt = workbook.add_format({ 'bold': True, 'bg_color': '#ffffaa' })
    reqfmt.set_shrink()

    for n, name in enumerate(terms):
        term = Term.get(name)
        occurrences.write(0, n, term.name, reqfmt if term.name in config['required'] else recfmt)
        occurrences.write_comment(0, n,
                ("REQUIRED" if term.name in config['required'] else "RECOMMENDED")
                + "\n\n"
                + term.definition(language) + "\n\n" + term.example(language))
        width = len(term.name) + 6
        occurrences.set_column(0, n, width)

        if (term.name == 'basisOfRecord'):
            occurrences.data_validation(1, n, 1000000, n, {
                'validate': 'list',
                'source': [
                    'PreservedSpecimen',
                    'HumanObservation',
                    'FossilSpecimen',
                    'LivingSpecimen',
                    'HumanObservation',
                    'MachineObservation'
                ]
            })

        if(uuid in form and term == 'occurrenceID'):
            for row in range(1, 5000):
                occurrences.write(row, n,
                        "urn:uuid:" + str(uuid.uuid4()), overflow)
    if 'measurementorfact' in form:
        mof = workbook.add_worksheet("MeasurementOrFact")
        for n, name in enumerate(mofterms):
            term = Term.get(name)
            mof.write(0, n, term.name, reqfmt if term.name in config['required'] else recfmt)
            if term.example(language) and term.definition(language):
                mof.write_comment(0, n,
                    ("REQUIRED" if term.name in config['required'] else "RECOMMENDED")
                        + "\n\n"
                        + term.definition(language) + "\n\n" + term.example(language))
            width = len(term.name) + 6
            mof.set_column(0, n, width)
    workbook.close()
    with open(path, "rb") as f:
        sys.stdout.write(f.read())


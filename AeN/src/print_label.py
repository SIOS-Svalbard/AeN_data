#!/usr/local/bin/python2.7
# encoding: utf-8
'''
 -- Creates and prints labels for AeN

 This program enables the creation and printing of labels 



@author:     Pål Ell8ingsen

@copyright:  2018 UNIS. 


@contact:    pale@unis.no
@deffield    updated: Updated
'''

import sys
import os
import uuid

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.bubble import Bubble
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import BooleanProperty
from kivy.uix.label import Label
from kivy.properties import NumericProperty

from kivy.config import Config

__all__ = []
__version__ = 0.1
__date__ = '2018-05-25'
__updated__ = '2018-05-25'

DEBUG = 1
TESTRUN = 0
PROFILE = 0


def new_hex_uuid():
    """
    Generate a new hex UUID based on the host ID and time

    Returns
    ----------
    uuid : string
           uuid expressed as a hex value
    """
    return uuid.uuid1().hex  # Based on host ID and time


def create_label(uuid, text1, text2, text3, text4):

    zpl = '''
    CT~~CD,~CC^~CT~
    ^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR4,4~SD15^JUS^LRN^CI0^XZ
    ^XA
    ^MMT
    ^PW1228
    ^LL0295
    ^LS0
    ^BY110,110^FT51,125^BXN,5,200,22,22,1,~
    ^FH\^FD{0}^FS
    ^FT8,267^A0N,21,21^FH\^FD{4}^FS
    ^FT8,231^A0N,21,21^FH\^FD{3}^FS
    ^FT9,198^A0N,21,21^FH\^FD{2}^FS
    ^FT9,166^A0N,21,21^FH\^FD{1}^FS
    ^PQ1,0,1,Y^XZ'''.format(uuid, text1, text2, text3, text4)

    print(zpl)
    return zpl


class LimitText(TextInput):
    max_characters = NumericProperty(0)


class LabelWidget(AnchorLayout):

    pass


class LabelApp(App):

    def build(self):
        widget = LabelWidget()
        self.widget = widget
        return widget

    def print_label(self, *args):
        print("Printing label")
        text1 = self.widget.ids.text1.text
        text2 = self.widget.ids.text2.text
        text3 = self.widget.ids.text3.text
        text4 = self.widget.ids.text4.text

        create_label(new_hex_uuid(), text1, text2, text3, text4)


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''

    try:
        args = parse_options()
        Config.set('graphics', 'width', '300')
        Config.set('graphics', 'height', '300')
        Config.write()
        LabelApp().run()
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0


def parse_options():
    """
    Parse the command line options and return these. Also performs some basic
    sanity checks, like checking number of arguments.
    """
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (
        program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Pål Ellingsen on %s.

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

    USAGE
    ''' % (program_shortdesc, str(__date__))

    # Setup argument parser
    parser = ArgumentParser(description=program_license,
                            formatter_class=RawDescriptionHelpFormatter)
#     parser.add_argument('output', help='''The output file''')
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0,
                        help="set verbosity level [default: %(default)s]")
    parser.add_argument('-V', '--version', action='version',
                        version=program_version_message)

    # Process arguments
    args = parser.parse_args()

    if args.verbose > 0:
        print("Verbose mode on")

    return args

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    sys.exit(main())

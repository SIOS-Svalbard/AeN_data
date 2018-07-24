#!/usr/bin/env python3
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
import time
import uuid
import warnings
import socket
import datetime as dt

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
from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty
from kivy.uix.label import Label
from kivy.properties import NumericProperty

from kivy.config import Config

__all__ = []
__version__ = 0.1
__date__ = '2018-05-25'
__updated__ = '2018-07-05'

DEBUG = 1
TESTRUN = 0
PROFILE = 0


def new_hex_uuid():
    """
    Generate a new hex UUID based on the host MAC address and time

    Returns
    ----------
    uuid : string
           uuid expressed as a hex value
    """
    return str(uuid.uuid1())  # Based on host ID and time


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
#     zpl = '''
#     CT~~CD,~CC^~CT~
#     ^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR4,4~SD15^JUS^LRN^CI0^XZ
#     ^XA
#     ^MMT
#     ^PW331
#     ^LL1051
#     ^LS0
#     ^FT48,410^A0N,42,40^FH\^FD{1}^FS
#     ^BY66,66^FT116,622^BXN,3,200,22,22,1,~
#     ^FH\^FD{0}^FS
#     ^PQ1,0,1,Y^XZ'''.format(uuid, text1)

    print(zpl)
    return zpl


class LimitText(TextInput):
    """
    Overriding TextInput to enable a limited length text field

    Properties
    ----------

    max_characters : int
        The max number of characters

    inc_num : Boolean
        Should the number be increased after a run
    """

    max_characters = NumericProperty(0)
    inc_num = BooleanProperty(0)


class Alert(Popup):

    def __init__(self, title, text):
        super(Alert, self).__init__()
        content = AnchorLayout(anchor_x='center', anchor_y='bottom')
        content.add_widget(
            Label(text=text, halign='left', valign='top', color=[1, 1, 1, 1])
        )
        ok_button = Button(
            text='Ok', size_hint=(None, None), size=(50, 50))
        content.add_widget(ok_button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=True,
        )
        ok_button.bind(on_press=popup.dismiss)
        popup.open()


class LabelWidget(FloatLayout):

    def activate_checkbox(self, checkbox, id):
        if id == 'date':

            self.ids.text1.text = checkbox.active * dt.date.today().isoformat()
        elif id == 'test':

            self.ids.text2.text = checkbox.active * 'This is a test'
        elif id == 'inc_num':

            self.ids.text4.inc_num = True


class LabelApp(App):

    def build(self):
        widget = LabelWidget()
        self.widget = widget
        self.socket = None
        self.first_print = True

        return widget

    def on_stop(self, *args):
        print('Exiting')
        if self.socket:
            self.socket.close()
        return True

    def start_printer(self, ip):
        self.IP = ip
        self.PORT = 9100
        self.BUFFER_SIZE = 1024
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.IP, self.PORT))

    def send_to_printer(self, zpl):

        self.socket.send(bytes(zpl, "utf-8"))

    def print_label(self, *args):
        print("Printing label")
        if self.first_print:
            if self.widget.ids.ip.text != '':
                try:
                    self.start_printer(self.widget.ids.ip.text)
                except (ConnectionRefusedError, OSError):
                    Alert('Wrong IP', 'Please input a valid/correct IP')
                    return
            else:
                Alert('Need IP', 'Please input an IP')
                return
            # self.first_print = False

        text1 = self.widget.ids.text1.text
        text2 = self.widget.ids.text2.text
        text3 = self.widget.ids.text3.text
        text4 = self.widget.ids.text4.text
        for n in range(int(self.widget.ids.number.text)):

            zpl = create_label(new_hex_uuid(), text1, text2, text3, text4)
            # Increase number on prints
            if self.widget.ids.text4.inc_num:
                try:
                    text4 = str(int(text4) + 1)
                    self.widget.ids.text4.text = text4
                except ValueError:
                    warnings.warn(
                        "WARNING: Text line 4 is not a number, can't increment", UserWarning)

                    time.sleep(seconds / 1e6)  # Wait 1 us

            self.send_to_printer(zpl)
        # Stop socket after each run
        self.on_stop()

def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''

    try:
        args = parse_options()
        Config.set('graphics', 'width', '400')
        Config.set('graphics', 'height', '400')
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

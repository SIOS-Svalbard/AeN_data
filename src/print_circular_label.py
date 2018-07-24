#!/usr/bin/env python3
# encoding: utf-8
'''
 -- Creates and prints circular 10 mm labels for AeN

 This program enables the creation and printing of labels of the 10 mm 
 circular type



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

__all__ = []
__version__ = 0.1
__date__ = '2018-07-03'
__updated__ = '2018-07-05'

DEBUG = 1


def create_label():
    """
    Creates the ZPL code for the label with 4 uuids.
----------
    zpl : str
        The formatted ZPL code string that should be sent to the Zebra printer 
    """
    uuids = []
    for i in range(4):
        uuids.append(str(uuid.uuid1()))
        # Ensure that we are not generating them to fast
        time.sleep(1. / 1e6)  # 1 us

    zpl = '''
CT~~CD,~CC^~CT~
^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR4,4~SD30^JUS^LRN^CI0^XZ
^XA
^MMT
^PW650
^LL0100
^LS0
^BY88,88^FT65,119^BXN,3,200,22,22,1,~
^FH\^FD{0}^FS
^BY88,88^FT219,119^BXN,3,200,22,22,1,~
^FH\^FD{1}^FS
^BY88,88^FT373,119^BXN,3,200,22,22,1,~
^FH\^FD{2}^FS
^BY88,88^FT526,119^BXN,3,200,22,22,1,~
^FH\^FD{3}^FS
^PQ1,0,1,Y^XZ'''.format(uuids[0], uuids[1], uuids[2], uuids[3])


    del uuids

    return zpl


def print_labels(args):

    PORT = 9100
    BUFFER_SIZE = 1024
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.ip, PORT))

    for ii in range(args.N // 4):
        zpl = create_label()
        if args.verbose > 0:
            print(zpl)

        sock.send(bytes(zpl, "utf-8"))

    sock.close()


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''

    try:
        args = parse_options()
        print_labels(args)
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
    parser.add_argument('N', type=int, help='''Set the number of labels to be printed,
if not a multiple of 4 will be rounded up to a multiple of ''' )
    parser.add_argument('ip',  type=str,
                        help="Set the IP of the printer, format is '192.168.1.1'")

    # Process arguments
    args = parser.parse_args()

    # Round up to nearest multiple of 4
    args.N = args.N + (args.N % 4)
    if args.verbose > 0:
        print("Verbose mode on")

    return args

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    sys.exit(main())

#!/usr/bin/python3
# encoding: utf-8
'''
 -- Creates pdf files for generating uuid labels



It defines classes_and_methods

@author:     Pål Ellingsen



@contact:    pale@unis.no
@deffield    updated: Updated
'''

import sys
import os
import qrcode
import uuid
from elaphe import barcode
from PIL import Image, ImageFont, ImageDraw
from fpdf import FPDF

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from io import BytesIO


__all__ = []
__version__ = 0.1
__date__ = '2018-05-02'
__updated__ = '2018-05-22'

DEBUG = 0


def new_hex_uuid():
    """
    Generate a new hex UUID based on the host ID and time


    Returns
    ----------
    uuid : string
           uuid expressed as a hex value
    """
    return uuid.uuid1().hex  # Based on host ID and time


class QR(object):
    """
    QR class for holding the paramters needed to generate the QR code

    """

    def __init__(self):
        """
        Initialises the QR class
        """
        self.qr = qrcode.QRCode(
            version=3,  # 37 x 37 elements, 352 bits information
            # 15 % correction
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=4,  # px per box
            border=4,  # boxes for border (min is 4)
        )  # This gives a total size of 370 * 370 px

    def qr_image(self, uuid):
        """
        Creates a Pillow QR image of a given uuid

        Parameters
        ----------
        uuid : string
                The input string for the QR code

        Returns
        ----------
        img : Pillow image
                The QR code image
        """
        self.qr.clear()
        self.qr.add_data(uuid)
        self.qr.make(fit=False)
        return self.qr.make_image()


def dm_image(uuid, scale, dpi):
    """
    Creates a Pillow Datamatrix image of a given uuid

    Parameters
    ----------
    uuid : string
            The input string for the 2D code

    Returns
    ----------
    img : Pillow image
            The Datamatrix code image
    """
    img = barcode('datamatrix', uuid, options=dict(format='square', version='22x22'),
                  data_mode='8bits', margin=0, scale=scale, dpi=dpi)
#     img.save("/export-b/work/Test.eps", "EPS")
    return img


class PDF(FPDF):

    def load_resource(self, reason, filename):
        return filename


def make_page(pdf, dpi):
    """
    Makes an A4 page and fills it with QR codes

    Returns
    ----------
    page : Pillow image
            The A4 page image

    """

    inch = 25.4  # mm
    qr = QR()

# # CILS eppendorf
#     # Margins
#     top = 7
#     side = 9
#
#     # Label size
#     lwidth = 25
#     lheight = 57
#
#     # Spacing
#     hpitch = 28
#     vpitch = 71
#
#     # number
#     cols = 7
#     rows = 4

# CILS Larger
    # Margins
    top = 10
    side = 10

    # Label size
    lwidth = 51
    lheight = 25

    # Spacing
    hpitch = 68
    vpitch = 28

    # number
    cols = 3
    rows = 2  # 10

#     # Smaller
#     # Margins
#     top = 10.5
#     side = 4.0
#
#     # Label size
#     lwidth = 38
#     lheight = 21
#
#     # Spacing
#     hpitch = 40.7
#     vpitch = 21
#
#     # number
#     cols = 5
#     rows = 13


#     # Avery L7152
#     # Margins
#     top = 13.7 / inch * dpi
#     side = 4.7 / inch * dpi
#
#     # Label size
#     lwidth = 99.1 / inch * dpi
#     lheight = 33.9 / inch * dpi
#
#     # Spacing
#     hpitch = 101.9 / inch * dpi
#     vpitch = 33.9 / inch * dpi
#
#     # number
#     cols = 2
#     rows = 8

    # Padding for the QR
    pad = 5

    cell_size = 0.35   # mm
    scale = cell_size / inch * dpi / 2 * 24 / 22
    print("Scale", scale)
    # Make page
    pdf.add_page()
#     page = Image.new('L', (int(width), int(height)), 'white')
#     font = ImageFont.truetype(
#         "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf", 20)
#     draw = ImageDraw.Draw(page)
    for r in range(rows):  # Loop over the rows
        for c in range(cols):  # Loop over the columns
            b = BytesIO()  # For saveing file
            uuid = new_hex_uuid()
            print(uuid)
#             img = qr.qr_image(uuid)
            img = dm_image(uuid, scale=scale, dpi=dpi)
            img.save(b, format='PNG', resolution=dpi)
            b.seek(0)
            pdf.image(
                b, x=int(side + (c * hpitch) + pad), y=int(top + (r * vpitch) + pad), w=img.size[0] / inch, h=img.size[1] / inch, type='PNG')
#             page.paste(
#                 img, box=(int(side + (c * hpitch) + pad), int(top + (r * vpitch) + pad)))
#
#             draw.text(
#                 (int(side + (c * hpitch) + pad),
#                  int(top + (r * vpitch) + 5 * pad + img.size[0])),
#                 uuid, (0), font=font)
#     return page


def save_pages(url, N=1):
    """
    Saves multiple pages of QR codes to a pdf file

    Parameters
    ----------

    url : string
        The output file

    N : int
        The number of pages wanted
        Default :1

    """
#     pages = []
    dpi = 600
    pdf = PDF('P', 'mm', 'A4')
#     first = make_page(dpi)
#     if N > 1:
    for ii in range(N):
        make_page(pdf, dpi)

    pdf.output(url + '.pdf', 'F')
#     pdf.save(url + '.pdf', "PDF", resolution=dpi,
#              save_all=True, append_images=pages, )
#     else:
#         first.save(url + '.pdf', "PDF", resolution=dpi)


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''

    try:
        args = parse_options()
        output = args.output
        save_pages(output, N=args.n)
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
    parser.add_argument('output', help='''The output file''')
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0,
                        help="set verbosity level [default: %(default)s]")
    parser.add_argument('-V', '--version', action='version',
                        version=program_version_message)
    parser.add_argument(
        '-n', dest='n', default=1, type=int, help="Set the number of pages wanted, [default: %(default)s]")

    # Process arguments
    args = parser.parse_args()

    if args.verbose > 0:
        print("Verbose mode on")

    return args

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    sys.exit(main())

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

# This script has been tested and developed for Python 2.7.
# It should be simple to convert it to Python 3.
# It should be even better to convert it to Python 3.4.
#
# This script does not require any external library.
#
# Want to extract all embedded images from all SVG files from your system?
# locate .svg | while read f ; do [ -f "$f" ] && grep -l 'xlink:href.*data:' "$f" ; done | while read f ; do ./extract_embedded_images_from_svg.py -p tmp/`basename "$f"`- "$f" ; done

from __future__ import division
from __future__ import print_function

import argparse
import base64
import errno
import io
import re
import os
import os.path
import sys
import xml.etree.ElementTree
import textwrap
import urllib


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Extracts all embedded images inside an SVG file.',
        epilog=textwrap.dedent('''
        SVGZ (compressed SVG) files are not supported directly, uncompress them first:
        gunzip -c foobar.svgz | {0} -

        For extracting images from PDF files, try 'pdfimages -j' from poppler package.
        '''.format(os.path.basename(sys.argv[0]))),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-p', '--prefix',
        action='store',
        help='prefix when saving the extracted images (default: the SVG pathname)'
    )
    parser.add_argument(
        'svgfile',
        action='store',
        type=argparse.FileType('rb'),
        help='the SVG file containing embedded images'
    )
    args = parser.parse_args()

    return args


# http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
# In Python 3.2, this piece of code can be replaced by a single line.
def mkdir_p(path):
    # For Python 3.2 or later:
    # os.makedirs(path, exist_ok=True)

    # For Python 2:
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def decode_data_url(url):
    # In Python 3.4, urllib.request already supports data URLs.
    # http://hg.python.org/cpython/rev/a182367eac5a
    # return urllib.request.urlopen(data_url).read()
    #
    # For earlier Python, we still need this function here.

    # The code below is based on:
    # http://hg.python.org/cpython/file/8fe3022af4b3/Lib/urllib/request.py

    scheme, data = url.split(':', 1)
    if scheme != 'data':
        return None, None

    mediatype, data = data.split(',', 1)

    # Even base64 encoded data URLs might be quoted so unquote in any case:
    # data = urllib.parse.unquote_to_bytes(data)  # For Python 3
    data = urllib.unquote(data)  # For Python 2.7
    if mediatype.endswith(';base64'):
        # data = base64.decodebytes(data)  # For Python 3
        data = base64.decodestring(data)  # For Python 2.7
        mediatype = mediatype[:-7]

    if not mediatype:
        mediatype = "text/plain;charset=US-ASCII"

    # Discarding the charset information.
    mediatype = mediatype.partition(';')[0]

    return data, mediatype


# Based on:
# https://github.com/django/django/blob/e2ae8b048e7198428f696375b8bdcd89e90002d1/django/utils/text.py#L213
def get_valid_filename(s):
    s = s.strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def stripNS(s):
    '''Receives either a tag name or an attribute name, returns the name
    without the namespace.

    >>> stripNS('{http://www.w3.org/2000/svg}image')
    'image'
    >>> stripNS('id')
    'id'
    '''
    return s.rpartition('}')[2]


def extract_from_svg(svgfile, prefix):
    # Creating dirs for prefix.
    parts = prefix.rpartition('/')
    prefix_dir = parts[0] + parts[1]
    prefix_file = parts[2]
    if prefix_dir:
        mkdir_p(prefix_dir)

    image_count = 0

    mime_to_extension = {
        'image/gif': '.gif',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/svg+xml': '.svg',  # Inception!?
    }

    for (event, elem) in xml.etree.ElementTree.iterparse(svgfile, ['start']):
        tag = stripNS(elem.tag)
        if tag == 'image':
            attrs = {stripNS(k): v for k, v in elem.attrib.items()}
            if 'href' in attrs:
                url = attrs['href']
                if url.startswith('data:'):
                    data, mimetype = decode_data_url(url)
                    image_count += 1
                    sane_id = get_valid_filename(attrs.get('id', ''))
                    extension = mime_to_extension.get(mimetype, '')
                    out_filename = '{0}{1}{2}{3}'.format(
                            prefix,
                            image_count,
                            '-' + sane_id if sane_id else '',
                            extension)
                    with open(out_filename, 'wb') as out:
                        out.write(data)


def main():
    options = parse_arguments()
    if options.prefix is None:
        options.prefix = options.svgfile.name if options.svgfile.name != '<stdin>' else 'stdin'

    extract_from_svg(options.svgfile, options.prefix)


if __name__ == "__main__":
    main()

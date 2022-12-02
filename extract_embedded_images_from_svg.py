#!/usr/bin/env python
# vi:ts=4 sw=4 et

# This script requires Python 3.4 or later.
# If you need to run it on earlier versions (why would you?), then please
# check the git history for an older implementation of this script.
#
# This script does not require any external library.
#
# Want to extract all embedded images from all SVG files from your system?
# locate .svg | while read f ; do [ -f "$f" ] && grep -l 'xlink:href.*data:' "$f" ; done | while read f ; do ./extract_embedded_images_from_svg.py -p tmp/`basename "$f"`- "$f" ; done

import argparse
import re
import os
import os.path
import sys
import textwrap
import urllib.request

# Consider using defusedxml module if deploying this on production.
import xml.etree.ElementTree


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


def decode_data_url(url):
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URLs
    # Default media type for data URLs.
    # It's nonsensical in the context of this script, though.
    mediatype = 'text/plain'

    match = re.match(r'^data:([^,;]+)', url)
    if match:
        mediatype = match.group(1)

    return urllib.request.urlopen(url).read(), mediatype


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
        os.makedirs(prefix_dir, exist_ok=True)

    image_count = 0

    mime_to_extension = {
        # https://developer.mozilla.org/en-US/docs/Web/SVG/Element/image
        # “The only image formats SVG software must support are JPEG, PNG, and
        # other SVG files. Animated GIF behavior is undefined.”
        'image/gif': '.gif',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/svg+xml': '.svg',  # Inception!?
        # To make this script future-proof, I'm adding a few extra image types.
        # These do not happen in the wild yet (or ever), and are likely
        # unsupported by most tools.
        'image/avif': '.avif',
        'image/bmp': '.bmp',
        'image/tiff': '.tif',
        'image/vnd.microsoft.icon': '.ico',
        'image/webp': '.webp',
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

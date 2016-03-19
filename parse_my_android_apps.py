#!/usr/bin/env python3
#
# This script will parse the HTML page that lists your Android apps in your
# Google Play Store. It will extract the data from the page and save it in
# easier-to-handle formats.
#
# Requirements:
#
# * Python 3 and `pyquery`
#         pip install pyquery
# * If you don't have `lxml` installed, you need to run
#   `apt-get install libxml2-dev libxslt1-dev` before `pip` can install `lxml`.
#
# How to use this script:
#
# 1. Open your browser and go to https://play.google.com/apps
# 2. Make sure you are logged in, of course.
# 3. Save the page (Ctrl+S) to your local machine. Make sure you select
#    "Webpage, Complete", so that it will also save the images.
# 4. Run this script:
#         ./parse_my_android_apps.py "My Android Apps - Google Play.html"
# 5. It will generate 3 files (and overwrite them if they exist):
#     * `<prefix>.csv` - Ready to be imported into a spreadsheet or into
#        [Google Fusion Tables](https://www.google.com/fusiontables/).
#     * `<prefix>.json` - JSON format.
#     * `<prefix>_simple.html` - More lightweight list of your apps.

import csv
import json
import re
import textwrap
from pyquery import PyQuery


def extract_info_from_card(card):
    card = PyQuery(card)
    ret = {}

    ret['appid'] = card.attr('data-docid')

    img = card.find('.cover-image-container img.cover-image')
    ret['img-large'] = img.attr('data-cover-large')
    ret['img-small'] = img.attr('data-cover-small')
    ret['img-local'] = img.attr('src')

    ret['page'] = card.find('a.card-click-target').attr('href')
    ret['title'] = card.find('.details h2 .title').attr('title')

    ret['developer-page'] = card.find('.details a.subtitle').attr('href')
    ret['developer'] = card.find('.details .subtitle').attr('title')

    description = card.find('.description').html()
    description = re.sub(r'<span class="paragraph-end".*', '', description)
    description = re.sub(r'<br\s*/?>', '\n', description)
    description = re.sub(r'</?p\s*/?>', '\n\n', description)
    description = '\n'.join(line.strip() for line in description.splitlines())
    description = re.sub(r'\n\n\n+', '\n\n', description)
    ret['description'] = description

    rating_style = card.find('.reason-set .current-rating').attr('style')
    rating_match = re.match(r'.*width:\s*([0-9.]+%).*', rating_style)
    ret['rating'] = rating_match.group(1) if rating_match else None

    return ret


def parse_filename(inputfile):
    q = PyQuery(filename=inputfile)
    parsed = [
        extract_info_from_card(card)
        for card in q('.card-list .card')
    ]
    return parsed


def main():
    import os.path
    import sys
    inputfile = sys.argv[1]
    parsed = parse_filename(inputfile)

    jsonfilename = os.path.splitext(inputfile)[0] + '.json'
    with open(jsonfilename, 'w', newline='') as f:
        json.dump(parsed, f, indent='\t')

    fields = [
        'appid',
        'title',
        'developer',
        'rating',
        'description',
        'page',
        'developer-page',
        'img-local',
        'img-small',
        'img-large',
    ]
    csvfilename = os.path.splitext(inputfile)[0] + '.csv'
    with open(csvfilename, 'w', newline='') as f:
        csvwriter = csv.DictWriter(f, fields)
        csvwriter.writeheader()
        csvwriter.writerows(parsed)

    htmlsimplefilename = os.path.splitext(inputfile)[0] + '_simple.html'
    with open(htmlsimplefilename, 'w', newline='') as f:
        f.write(textwrap.dedent('''\
            <!DOCTYPE html>
            <head>
            <meta charset="utf8">
            <title>My Android apps</title>
            <style type="text/css">
            html, body {
            }
            a img { border: 0; }
            a { text-decoration: none; }
            .app {
                position: relative;
                display: inline-block;
                overflow: hidden;
                width: 20em;
                height: 10em;
                padding: 4px;
                background: white;
                color: black;
                border: 1px solid #CCC;
                margin: 2px;
            }
            .app h1,
            .app h2,
            .app h3,
            .app figure {
                margin: 0;
                padding: 0;
                font: inherit;
            }
            .app h1 { font-weight: bold; }
            .app h2 { font-style: italic; }
            .app figure,
            .app .rating {
                float: left;
                clear: left;
                margin-right: 4px;
            }
            .app figure img,
            .app .rating {
                width: 2em;
            }
            .app .description {
                font-size: 0.75em;
                color: #444;
                white-space: pre-wrap;
            }
            </style>
            </head>
            <body>
            '''))
        for app in parsed:
            rating = app['rating']
            rating_number = float(rating[:-1])
            rating_number = round(rating_number, 1)
            f.write(textwrap.dedent('''\
                <div class="app">
                    <figure><a href="{page}"><img src="{img-local}" alt=""></a></figure>
                    <div class="rating">{rating_number}</div>

                    <h3><a href="{page}">{appid}</a></h3>
                    <h1><a href="{page}">{title}</a></h1>
                    <h2><a href="{developer-page}">{developer}</a></h2>

                    <div class="description">{description}</div>

                </div>
                '''.format(rating_number=rating_number, **app)))
        f.write(textwrap.dedent('''\
            </body>
            </html>
            '''))


if __name__ == '__main__':
    main()

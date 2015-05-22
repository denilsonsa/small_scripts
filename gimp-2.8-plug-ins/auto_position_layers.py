#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

# Tested on Gimp 2.8.14 with Python 2.7
# http://www.gimp.org/docs/python/index.html

import re
from gimpfu import *

def auto_position_layers(image, layer, auto_fit_canvas):
    #print '{0} {1}x{2} @ {3},{4}'.format(
    #    repr(layer),
    #    repr(layer.width), repr(layer.height),
    #    repr(layer.offsets[0]), repr(layer.offsets[1]),
    #)

    pdb.gimp_image_undo_group_start(image)

    gimp.progress_init('Moving around {0} layers'.format(len(image.layers)))
    progress = 0.0
    progress_increment = 1.0 / len(image.layers)

    RE = re.compile(r'.*_([0-9]+)_([0-9]+)(?:\.(?:jpg|png|gif|bmp|xpm))?$', re.I)
    for layer in image.layers:
        progress += progress_increment
        gimp.progress_update(progress)
        match = RE.match(layer.name)
        if match:
            x = int(match.group(1))
            y = int(match.group(2))
            layer.set_offsets(x * 256, y * 256)

    if auto_fit_canvas:
        pdb.gimp_image_resize_to_layers(image)

    pdb.gimp_image_undo_group_end(image)


# Parameters to register()
#   name
#   blurb
#   help
#   author
#   copyright
#   date
#   menupath
#   imagetypes
#     ""  (if the plugin doesn't need an image)
#     "*" (all image types)
#     "RGB*"
#     "RGB, RGBA"
#     "GRAY, GRAYA"
#     and maybe others
#   params
#     The tuple format is:
#     (type, name, description, default [, extra])
#   results
#   function

register(
    'auto_position_layers',
    'Auto-position layers based on coords in the name',
    'Auto-position layers based on coords in the name. Useful for fine-position screenshots and image tiles that have a precise naming . For fine-tuning the results, please edit the source-code.',
    u'Denilson Figueiredo de Sá',
    'Licensed under WTFPL',
    '2015-05-02',
    '<Image>/Image/Auto-position layers',
    '*',  # What are the possible image types?
    [
        (PF_BOOL, 'fit-canvas', '_Fit canvas to layers, after positioning them', True, None),
        #(PF_SPINNER, 'tile-width',  'Tile _Width',  16, (2,65536,2)),
        #(PF_SPINNER, 'tile-height', 'Tile _Height', 16, (2,65536,2)),
    ],
    [], # Results
    auto_position_layers
)

main()

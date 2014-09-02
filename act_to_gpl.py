#!/usr/bin/env python3
#
# Adobe Photoshop "*.act" palette file conversion to GIMP "*.gpl" palette
# format (which is also recognized by many other tools).
#
# How to use:
#   ./act_to_gpl.py some_palette.act > some_palette.gpl
#
# Code based on swatchbook/codecs/adobe_act.py from:
# http://www.selapa.net/swatchbooker/


import os.path
import struct
import sys


def parse_adobe_act(filename):
    filesize = os.path.getsize(filename)
    with open(filename, 'rb') as file:
        if filesize == 772:  # CS2
            file.seek(768, 0)
            nbcolors = struct.unpack('>H', file.read(2))[0]
            file.seek(0, 0)
        else:
            nbcolors = filesize // 3

        # List of (R, G, B) tuples.
        return [struct.unpack('3B',file.read(3)) for i in range(nbcolors)]


def return_gimp_palette(colors, name, columns=0):
    return 'GIMP Palette\nName: {name}\nColumns: {columns}\n#\n{colors}\n'.format(
        name=name,
        columns=columns,
        colors='\n'.join(
            '{0} {1} {2}\tUntitled'.format(*color)
            for color in colors
        ),
    )

if __name__ == '__main__':
    print(
        return_gimp_palette(parse_adobe_act(sys.argv[1]), sys.argv[1])
    )

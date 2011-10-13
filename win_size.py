#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

from __future__ import division
from __future__ import print_function

import argparse

# Easy way of importing pygame:
# import pygame

# Hard way of importing pygame:
import pygame.display
import pygame.event
import pygame.key

from pygame.locals import *


def set_size(width, height):
    screen = pygame.display.set_mode((width, height), RESIZABLE)

    size_string = '{0}x{1}'.format(width, height)
    pygame.display.set_caption(size_string)
    print(size_string)

    yellow = (255, 255, 0)
    screen.fill(yellow)

    pygame.display.flip()

def change_size(delta_width, delta_height):
    #pygame.display.get_surface().get_size()
    info = pygame.display.Info()
    w = info.current_w + delta_width
    h = info.current_h + delta_height
    set_size(w, h)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Opens a window with the specified size.',
        epilog='''This script uses Pygame to open a window painted with yellow
        color. Use arrow keys to increase/decrese the window dimensions. The
        current size <width>x<height> is shown at the window title, and also
        printed to the stdout. In order to understand why this script was
        written, read http://my.opera.com/CrazyTerabyte/blog/2011/10/13/nvidia-bug-when-rendering-windows-smaller-than-32x32''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'width',
        action='store',
        type=int,
        help='initial window width'
    )
    parser.add_argument(
        'height',
        action='store',
        type=int,
        help='initial window height'
    )
    args = parser.parse_args()
    return args

def main():
    options = parse_arguments()

    # pygame.init() will try to initialize all pygame modules, including
    # Cdrom and Audio. I'm not using such things, so let's initialize the
    # only really required module:
    pygame.display.init()
    set_size(options.width, options.height)

    # This does not work... :-(
    pygame.key.set_repeat(500, 50)

    key_and_offsets = {
        # Key: (delta_width, delta_height)
        K_UP:    ( 0, -1),
        K_DOWN:  ( 0, +1),
        K_LEFT:  (-1,  0),
        K_RIGHT: (+1,  0),
    }

    while True:
        event = pygame.event.wait()

        if event.type == QUIT:
            break

        elif event.type == KEYDOWN:
            if event.key in [K_ESCAPE, K_q]:
                break
            elif key_and_offsets.has_key(event.key):
                delta_width, delta_height = key_and_offsets.get(event.key)
                change_size(delta_width, delta_height)

        elif event.type == VIDEORESIZE:
            w, h = event.size
            set_size(w, h)

    pygame.quit()

if __name__ == '__main__':
    main()

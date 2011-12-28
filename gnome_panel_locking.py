#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

from __future__ import print_function

import argparse
import gconf
import sys


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Locks/unlocks all applets from a gnome panel.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-l', '--lock',
        action='store_true',
        help='lock all applets and panels'
    )
    parser.add_argument(
        '-u', '--unlock',
        action='store_true',
        help='unlock all applets and panels'
    )
    args = parser.parse_args()

    if args.lock and args.unlock:
        parser.exit('Use either --lock or --unlock, but not both.')
    elif (not args.lock) and (not args.unlock):
        parser.exit('Use either --lock or --unlock.')

    return args

def main():
    options = parse_arguments();

    # Value to be written
    if options.lock:
        locked_boolean = True
    elif options.unlock:
        locked_boolean = False
    else:
        print('Program error. This should not happen.')
        sys.exit(1)

    client = gconf.client_get_default()
    client.set_bool('/apps/panel/global/locked_down', locked_boolean)
    for path in client.all_dirs('/apps/panel/applets'):
        client.set_bool(path + '/locked', locked_boolean)

if __name__ == "__main__":
    main()

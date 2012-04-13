#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

from __future__ import print_function

import argparse
import gconf
import sys


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Locks/unlocks all panels and applets from a gnome panel. Tested with Gnome 2.30.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # Maybe the next line is a good solution, but it gave me an exception when I
    # tried to use it. Maybe I had an outdated argparse version.
    #parser.add_mutually_exclusive_group(required=True)
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
        parser.print_usage()
        parser.exit('error: Use either --lock or --unlock, but not both.')
    elif (not args.lock) and (not args.unlock):
        parser.print_usage()
        parser.exit('error: Use either --lock or --unlock.')

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
    for path in client.all_dirs('/apps/panel/objects'):
        client.set_bool(path + '/locked', locked_boolean)

if __name__ == "__main__":
    main()

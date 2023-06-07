#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

# Please consider using a better tool instead of this crappy script: https://github.com/eradman/entr

# TODO list:
#  * Add support for pyinotify (falling back to dumb polling if it's not
#    available)
#  * Add support for monitoring multiple files, instead of just one.

import getopt
import os
import os.path
import sys
import time


available_parameters = [
    ("h", "help", "Print help"),
    ("i:", "interval=", "Defines the polling interval, in seconds (default=1.0)"),
]


class ProgramOptions(object):
    """Holds the program options, after they are parsed by parse_options()"""

    def __init__(self):
        self.poll_interval = 1
        self.args = []


def print_help():
    scriptname = os.path.basename(sys.argv[0])
    print "Usage: {0} [options] filename".format(scriptname)
    print "Sleeps until 'filename' has been modified."
    print ""
    print "Options:"
    long_length = 2 + max(len(long) for x, long, y in available_parameters)
    for short, long, desc in available_parameters:
        if short and long:
            comma = ", "
        else:
            comma = "  "

        if short == "":
            short = "  "
        else:
            short = "-" + short[0]

        if long:
            long = "--" + long

        print "  {0}{1}{2:{3}}  {4}".format(short, comma, long, long_length, desc)

    print ""
    print "Currently, it is implemented using polling. In future, support for pyinotify might be added."
    print ""
    print "Sample usage command-line:"
    print "  while sleep_until_modified.py myfile.tex || sleep 1; do make ; done "


def parse_options(argv, opt):
    """argv should be sys.argv[1:]
    opt should be an instance of ProgramOptions()"""

    try:
        opts, args = getopt.getopt(
            argv,
            "".join(short for short, x, y in available_parameters),
            [long for x, long, y in available_parameters]
        )
    except getopt.GetoptError as e:
        print str(e)
        print "Use --help for usage instructions."
        sys.exit(2)

    for o, v in opts:
        if o in ("-h", "--help"):
            print_help()
            sys.exit(0)
        elif o in ("-i", "--interval"):
            opt.poll_interval = float(v)
        else:
            print "Invalid parameter: {0}".format(o)
            print "Use --help for usage instructions."
            sys.exit(2)

    opt.args = args
    if len(args) == 0:
        print "Missing filename"
        print "Use --help for usage instructions."
        sys.exit(2)
    if len(args) > 1:
        print "Currently, this script monitors only one file, but {0} files were given. Aborting.".format(len(args))
        sys.exit(2)


def main():
    opt = ProgramOptions()
    parse_options(sys.argv[1:], opt)

    file = opt.args[0]
    prev_time = os.stat(file).st_mtime
    while True:
        time.sleep(opt.poll_interval)
        new_time = os.stat(file).st_mtime
        if new_time != prev_time:
            break


if __name__ == "__main__":
    main()

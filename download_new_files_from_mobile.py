#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

# TODO list:
# * Create a ProgressLine class (or function) that prints the progress bar
#   alongside "value/max" numbers
#   * Is this really needed? Maybe it's better to use the "progressbar" module:
#     http://pypi.python.org/pypi/progressbar
#     http://code.google.com/p/python-progressbar/


from __future__ import division
from __future__ import print_function

import os
import os.path
import shutil
import sys
import time

from math import ceil


# TODO: Implement a nice module for getting the terminal size.
# * Should be similar to
#   http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
#   http://stackoverflow.com/questions/1022957/getting-terminal-width-in-c
#   https://github.com/cldwalker/hirb/blob/master/lib/hirb/util.rb#L61-71
# * Should have different methods of getting the size:
#   - using ioctl call
#   - calling either tput or stty
#   - reading COLUMNS and LINES environment variables
#   - fall-back to hard-coded default 80x24
# * Should cache the working method once, so that future "updates" would call
#   this method directly, instead of trying each one.
# * When should the module update the internal size cache?
#   - On every call. (reliable, but quite an overhead)
#   - Upon receiving SIGWINCH signal. (nice, very little overhead, but might
#     be undesirable)
#   - Manually. (a "force reload" or something must be called)
# * Find out how to get the size in Windows.

def test_sigwinch():
    # Note: signal handling will interrupt the sleep function.

    import signal
    signal.signal(signal.SIGWINCH, lambda signum, frame: print("SIGWINCH received"))

    time.sleep(10)
    print("slept")
    time.sleep(10)
    print("done")

    c = 0
    for i in xrange(10**8):
        c += 1
    print(c)

    return


def repeat_string(s, min_width):
    '''Repeats the string 's' to the desired 'min_width'.

    >>> repeat_string(".", 4)
    "...."
    >>> repeat_string("ab", 4)
    "abab"
    >>> repeat_string("ab", 5)
    "ababab"
    >>> repeat_string("ab", 6)
    "ababab"

    '''

    return s * int(ceil(min_width / len(s)))


class ProgressBar(object):
    '''Simple one-line ASCII-art progress bar.

    Instances of this class have "max" and "value" attributes, with roughly
    the same meaning as those attributes of <progress> element from HTML5.

    If "max" is zero or negative, then the progress bar is always complete.

    The user of this class is free to modify any instance attribute anytime.


    >>> pb = ProgressBar(max=10)
    >>> pb.columns = 13
    >>> pb.render()
    '[>          ]'
    >>> pb.value = 5
    >>> pb.render()
    '[=====>     ]'
    >>> pb.value = 10
    >>> pb.render()
    '[==========>]'

    >>> pb.prefix = "<<"
    >>> pb.filled = "*"
    >>> pb.infix  = "(@)"
    >>> pb.empty  = "."
    >>> pb.suffix = ">>"
    >>> pb.value = 0
    >>> pb.render()
    '<<(@)......>>'
    >>> pb.value = 5
    >>> pb.render()
    '<<***(@)...>>'
    >>> pb.value = 10
    >>> pb.render()
    '<<******(@)>>'

    >>> pb.columns=20
    >>> pb.prefix = "('')"
    >>> pb.filled = " [$]"
    >>> pb.infix  = "('<"
    >>> pb.empty  = " -"
    >>> pb.suffix = "('')"
    >>> pb.value = 0
    >>> pb.render()
    "('')('<- - - - -('')"
    >>> pb.value = 10
    >>> pb.render()
    "('') [$] [$] ('<('')"
    '''

    def __init__(self, max=1.0, value=0.0):
        self.max = max
        self.value = value

        # TODO: auto-detect the number of columns
        self.columns = 70  # Hardcoded, for now.

        self.out = sys.stdout  # Hardcoded... Might be stderr, huh?

        self.prefix = '['
        self.filled = '='
        self.infix  = '>'
        self.empty  = ' '
        self.suffix = ']'

    def render(self):
        "Renders the progress bar and returns it as string"

        width = self.columns - len(self.prefix) - len(self.infix) - len(self.suffix)

        if self.max > 0.0:
            filled_len = int(round(width * self.value / self.max))
        else:
            filled_len = width

        empty_len = width - filled_len

        return '{prefix}{0}{infix}{1}{suffix}'.format(
            repeat_string(self.filled, filled_len)[:filled_len],
            repeat_string(self.empty , empty_len )[-empty_len:],
            **self.__dict__
        )

    def print(self):
        "Prints the progress bar"

        self.out.write('\r' + self.render())
        self.out.flush()

    def erase(self):
        "Tries to erase the progress bar by printing spaces over it"

        self.out.write('\r' + (' ' * self.columns) + '\r')
        self.out.flush()


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description='Finds what files are missing on the destination directory and copy them.',
        epilog='This script was created to copy new photos from my mobile'
        ' phone over bluetooth. I first use "obexfs" program to mount the'
        ' mobile phone filesystem using "FUSE", and then I run this script to'
        ' copy the photos to a destination directory. Since my mobile phone'
        ' is a bit buggy, I need to add a delay before I start copying the'
        ' next file. Photos that already exist are skipped.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-t', '--test',
        action='store_true',
        dest='run_tests',
        help='Run the self-test (doctest) of this script (when using this option, supply any string as source_dir and dest_dir)'
    )
    parser.add_argument(
        '-n', '--dry-run', '--just-print',
        action='store_true',
        dest='dry_run',
        help='Don\'t actually copy the files, just print what would be copied'
        # TODO: maybe in this case the progress bar should not be printed, and
        # the files should not be prefixed with "Copying".
        # Anyway, this option is useful for debugging this script.
    )
    parser.add_argument(
        '-s', '--sleep',
        action='store',
        default=0,
        type=int,
        metavar='SECONDS',
        dest='sleep_seconds',
        help='Sleep this amount of seconds between each file'
    )
    parser.add_argument(
        'source_dir',
        action='store',
        type=str,
        help='Copy files from this directory'
    )
    parser.add_argument(
        'dest_dir',
        action='store',
        type=str,
        help='Copy files to this directory'
    )

    options = parser.parse_args()

    if not options.run_tests:
        # TODO: Implement a better handling of non-existent destination
        # directory (auto-create it if user passes a parameter)

        for dir in [options.source_dir, options.dest_dir]:
            if not os.path.isdir(dir):
                parser.exit(u'Directory "{0}" not found'.format(dir))

    return options


def main():

    options = parse_args()

    if options.run_tests:
        import doctest
        doctest.testmod()

    else:
        source_dir = options.source_dir
        dest_dir = options.dest_dir

        # Finding the file lists
        source_files = set(
            f for f in os.listdir(source_dir)
            if os.path.isfile(os.path.join(source_dir, f))
        )
        dest_files = set(
            f for f in os.listdir(dest_dir)
            if os.path.isfile(os.path.join(dest_dir, f))
        )
        missing_files = source_files - dest_files

        # DEBUG:
        #print("source_dir: {}\n{}\ndest_dir: {}\n{}".format(source_dir, source_files, dest_dir, dest_files))

        # Printing overall quantities
        print("Source files: {0}; Destination files: {1}; Missing files: {2}"
            .format(
                len(source_files),
                len(dest_files),
                len(missing_files)
            )
        )

        progress = ProgressBar(len(missing_files))
        for f in sorted(missing_files):
            print(u'Copying {0}'.format(f))
            progress.print()

            if not options.dry_run:
                shutil.copy2(os.path.join(source_dir, f), dest_dir)

            if options.sleep_seconds:
                time.sleep(options.sleep_seconds)

            progress.erase()
            progress.value += 1

        # Printing the final, completed progress bar. Just to give a warm feeling
        # to the user. :)
        progress.print()
        print()


if __name__ == "__main__":
    main()

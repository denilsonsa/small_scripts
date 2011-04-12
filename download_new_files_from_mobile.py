#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

# TODO list:
# * Receive source_dir and dest_dir from parameters
# * Write a --help description
# * Add a "wait" parameter that inserts a time.sleep() after each copied file
#   (I need it for my SE-K750i)
# * Create a ProgressLine class (or function) that prints the progress bar
#   alongside "value/max" numbers



from __future__ import division
from __future__ import print_function

# TODO: add getopt...
#import getopt

import os
import os.path
import shutil
import sys
import time


class ProgressBar(object):
    '''Simple one-line ASCII-art progress bar.

    Instances of this class have "max" and "value" attributes, with roughly
    the same meaning as those attributes of <progress> element from HTML5.

    If "max" is zero or negative, then the progress bar is always complete.

    The user of this class is free to modify any instance attribute anytime.
    '''

    def __init__(self, max=1.0, value=0.0):
        self.max = max
        self.value = value

        # TODO: auto-detect the number of columns
        self.columns = 70  # Hardcoded, for now.

        self.out = sys.stdout  # Hardcoded... Might be stderr, huh?

        self.prefix = '['
        self.filled = '='  # TODO: Allow this to have multiple chars
        self.infix  = '>'
        self.empty  = ' '  # TODO: Allow this to have multiple chars
        self.suffix = ']'

    def render(self):
        "Renders the progress bar and returns it as string"

        width = self.columns - len(self.prefix) - len(self.infix) - len(self.suffix)

        if self.max > 0.0:
            filled = int(round(width * self.value / self.max))
        else:
            filled = width

        empty = width - filled

        return '{prefix}{0}{infix}{1}{suffix}'.format(
            self.filled * filled,
            self.empty * empty,
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


def main():
    source_dir = os.path.expanduser(u'~/btnokia/E:/Images')
    dest_dir = os.path.expanduser(u'~/scripts/testing')

    # TODO: Implement a better handling of non-existent destination directory
    for dir in [source_dir, dest_dir]:
        if not os.path.isdir(dir):
            print(u'Directory "{0}" not found'.format(dir))
            sys.exit(1)

    source_files = set(
        f for f in os.listdir(source_dir)
        if os.path.isfile(os.path.join(source_dir, f))
    )
    dest_files = set(
        f for f in os.listdir(dest_dir)
        if os.path.isfile(os.path.join(dest_dir, f))
    )
    missing_files = source_files - dest_files

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
        shutil.copy2(os.path.join(source_dir, f), dest_dir)
        #time.sleep(4)
        progress.erase()
        progress.value += 1

    # Printing the final, completed progress bar. Just to give a warm feeling
    # to the user. :)
    progress.print()
    print()


if __name__ == "__main__":
    main()

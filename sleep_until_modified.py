#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import os
import sys
import time


def main():
    file = sys.argv[1]
    prev_time = os.stat(file).st_mtime
    poll_interval = 1
    while True:
        time.sleep(poll_interval)
        new_time = os.stat(file).st_mtime
        if new_time != prev_time:
            break


if __name__ == "__main__":
    main()

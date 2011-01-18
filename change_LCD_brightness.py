#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import os
import os.path
import subprocess
import sys

# Old, deprecated /proc/acpi path
HARDCODED_PATH = "/proc/acpi/video/VGA/LCDD/brightness"
# New, /sys path
# However... This script must be rewritten to work with /sys/ interface
# HARDCODED_PATH = "/sys/class/backlight/acpi_video0/brightness"

HARCODED_SUDO_SCRIPT = "/usr/local/bin/set_lcd_brightness.sh"
# The script contents:
# #!/bin/sh
# echo "$1" > /proc/acpi/video/VGA/LCDD/brightness
#
# The relevant /etc/sudoers line:
# %users ALL = NOPASSWD: /usr/local/bin/set_lcd_brightness.sh

def print_help():
    scriptname = os.path.basename(sys.argv[0])
    print (
        "Usage: {name} [+|-]value\n"
        "Examples:\n"
        "  {name} +1   # Increase brightness\n"
        "  {name} 10   # Set brightness to exactly 10\n"
    ).format(name=scriptname)

    levels, current = parse_proc_brightness()
    print "Current brightness: {0}".format(current)
    print "Available brightness levels:"
    print " ".join(levels)

def parse_proc_brightness():
    levels = []
    current = None
    with open(HARDCODED_PATH, "rb") as f:
        for line in f:
            key, sep, value = line.partition(":")
            if key == "levels":
                levels = value.split()
            elif key == "current":
                current = value.strip()

    return levels, current

def main():
    if len(sys.argv) != 2:
        print_help()
        sys.exit(1)

    value_str = sys.argv[1]
    value = int(value_str)
    relative = value_str[0] in "+-"

    if relative:
        levels, current = parse_proc_brightness()
        index = levels.index(current)
        new_index = index + value

        #if new_index < 0:
        #    new_index = 0
        #if new_index >= len(levels):
        #    new_index = len(levels) - 1
        new_index = max(0, min(new_index, len(levels)-1))

        new_value = levels[new_index]

    else:
        new_value = str(value)

    try:
        # Can we write directly to that file?
        with open(HARDCODED_PATH, "wb") as f:
            f.write(new_value)
    except IOError:
        # So we can't write to it... But at least we have a sudo script.
        subprocess.call(["sudo", "-n", HARCODED_SUDO_SCRIPT, new_value])

    # Optional xosd support
    # It works, but I didn't like it. Feel free to uncomment if you want.
    #
    #try:
    #    xosd_args = "osd_cat -A center -p bottom -o 32 -c green -O 1 -u black -b percentage -P".split()
    #    percentage = 100 * new_index / (len(levels)-1)
    #    xosd_args.append(str(int(round(percentage))))
    #    subprocess.call(["killall", "osd_cat"])
    #    subprocess.Popen( xosd_args )
    #except:
    #    pass


if __name__ == "__main__":
    main()

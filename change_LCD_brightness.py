#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import os
import os.path
import subprocess
import sys


# Lots of things here are hard-coded...
# This script is a bit ugly, but works.
# And it evolved from a version that worked with /proc/acpi path (and that
# explains a bit of the ugliness).


# Old, deprecated /proc/acpi path
#HARDCODED_PROC_PATH = "/proc/acpi/video/VGA/LCDD/brightness"

# New, /sys path
HARDCODED_SYS_PATH = "/sys/class/backlight/acpi_video0/"

BRIGHTNESS_PATH = os.path.join(HARDCODED_SYS_PATH, "brightness")
MAX_BRIGHTNESS_PATH = os.path.join(HARDCODED_SYS_PATH, "max_brightness")


HARDCODED_SUDO_SCRIPT = "/usr/local/bin/set_lcd_brightness.sh"
# The script contents:
# #!/bin/sh
# echo "$1" > /sys/class/backlight/acpi_video0/brightness
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

    levels, current = parse_sys_brightness()
    print "Current brightness: {0}".format(current)
    print "Available brightness levels:"
    print " ".join(levels)


def parse_sys_brightness():
    with open(MAX_BRIGHTNESS_PATH, "rb") as f:
        max_brightness = int(f.readline())

    levels = [str(x) for x in range(max_brightness+1)]

    with open(BRIGHTNESS_PATH, "rb") as f:
        current = f.readline().strip()

    return levels, current


def main():
    if len(sys.argv) != 2:
        print_help()
        sys.exit(1)

    value_str = sys.argv[1]
    value = int(value_str)
    relative = value_str[0] in "+-"

    if relative:
        levels, current = parse_sys_brightness()
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
        with open(BRIGHTNESS_PATH, "wb") as f:
            f.write(new_value)
    except IOError:
        # So we can't write to it... But at least we have a sudo script.
        subprocess.call(["sudo", "-n", HARDCODED_SUDO_SCRIPT, new_value])

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

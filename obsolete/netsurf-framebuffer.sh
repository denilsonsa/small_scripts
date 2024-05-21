#!/bin/sh
#
# Trivial wrapper script to run netsurf browser on the framebuffer, without X11.
# I used it once on a Raspberry Pi as a lightweight web browser.
# Unfortunately, running stuff on the framebuffer isn't a good experience, as
# it is much more limited than a full desktop, and it's a use-case rarely
# tested by anyone.

# http://source.netsurf-browser.org/netsurf.git/tree/docs/netsurf-fb.1
# https://manpages.debian.org/stretch/netsurf-fb/netsurf.1

# Try these options:
# --block_advertisements
# --animate_images
# --show_single_tab
exec netsurf-fb --window_width 1920 --window_height 1080 "$@"

#!/bin/sh

# On some distros or some computers, the Win key (between Ctrl and Alt)
# doesn't work as I expect. Since I use it for basically all my Window Manager
# shortcuts, I need it working.
#
# This command "fixes" that key, making it work the way I expect.

setxkbmap -variant altwin:super_win

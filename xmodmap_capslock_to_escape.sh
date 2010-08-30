#!/bin/sh

# Removing the Caps Lock modifier, and then remapping to Escape
xmodmap -e 'clear lock' -e 'keycode 66 = Escape'

# References:
# http://www.in-ulm.de/~mascheck/X11/xmodmap.html
# http://superuser.com/questions/53092/gnome-map-altgr-key-to-alt
# http://superuser.com/questions/138708/xorg-how-can-i-map-altgr-to-the-capslock-key-to-toggle-3rd-level-symbols
# http://superuser.com/questions/16070/vim-command-to-map-capslock-to-escape

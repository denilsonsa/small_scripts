#!/bin/sh

# Remapping the "(Context) Menu" key to Compose key (AKA Multi_Key)
xmodmap -e 'keycode 135 = Multi_key'
# Other solution:
#xmodmap -e 'keysym Menu = Multi_key'

# See the list of compose sequences:
# /usr/share/X11/locale/en_US.UTF-8/Compose
#
# Wanna create your own sequences? Read this:
# http://xorg.freedesktop.org/releases/X11R7.1/doc/RELNOTES4.html#30

# References:
# http://soft.zoneo.net/Linux/compose_key.php#xmodmap
#
# http://wa5pb.freeshell.org/motd/?p=382
# http://superuser.com/questions/154303/is-there-a-us-international-keyboard-layout-on-linux-that-mimics-windows-behavio
#
# https://help.ubuntu.com/community/ComposeKey
# http://en.wikipedia.org/wiki/Compose_key
# http://hermit.org/Linux/ComposeKeys.html

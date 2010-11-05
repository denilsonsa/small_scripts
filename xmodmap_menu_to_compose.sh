#!/bin/sh

# Remapping the "(Context) Menu" key to Compose key (AKA Multi_Key)
xmodmap -e 'keycode 135 = Multi_key'
# Other solution:
#xmodmap -e 'keysym Menu = Multi_key'

# See the list of compose sequences:
# /usr/share/X11/locale/en_US.UTF-8/Compose
#
# See also: man Compose(5)
#
# Detailed information on my blog:
# http://my.opera.com/CrazyTerabyte/blog/2010/11/04/how-x11-xcompose-works

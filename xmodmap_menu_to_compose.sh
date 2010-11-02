#!/bin/sh

# Remapping the "(Context) Menu" key to Compose key (AKA Multi_Key)
xmodmap -e 'keycode 135 = Multi_key'

# References:
# http://soft.zoneo.net/Linux/compose_key.php#xmodmap
#
# https://help.ubuntu.com/community/ComposeKey
# http://en.wikipedia.org/wiki/Compose_key
# http://hermit.org/Linux/ComposeKeys.html

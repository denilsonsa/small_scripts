#!/bin/sh

# This script is inspired by xmodmap_logitech_mouse_buttons.sh

# 1b1c:1b3c Corsair
#    _______
#   /  | |  \   Scroll:
#  | 1 |2| 3 |    4
#  |   |_|   |  6<@>7
#  |         |    5
# []9 Forward|
#  |         |
# []8 Back   |
#  |         |
#   \_______/


# Changes:
# * Side buttons are now horizontal scroll (8,9 = 6,7)

MOUSE_ID=`xinput list | sed -n 's/.*Corsair Gaming HARPOON RGB Mouse.*id=\([0-9]\+\)[^0-9].*slave \+pointer.*/\1/p'`

if [ -z "$MOUSE_ID" ] ; then
  echo 'Corsair HARPOON RGB Mouse not found'
  exit 1
fi

xinput set-button-map "$MOUSE_ID" 1 2 3 4 5 6 7 6 7

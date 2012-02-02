#!/bin/sh

# 046d:c049 Logitech, Inc. G5 Laser Mouse
#    _______
#   /  | |  \   Scroll:
#  | 1 |2| 3 |    4
#  |   |_|   |  6<@>7
#  |         |    5
# []9        |
#  |         |
# []8        |
#  |         |
#   \_______/


# Changes:
# * Vertical scrolling is reversed (4<->5)
# * Horizontal scrolling is reversed (6<->7)
# * Side buttons are now middle-click (8,9 = 2)

# For some reason, this command is giving me:
#xmodmap -e 'pointer = 1 2 3 5 4 7 6 2 2'
# X Error of failed request:  BadValue (integer parameter out of range for operation)
#   Major opcode of failed request:  116 (X_SetPointerMapping)
#   Value in failed request:  0x2
#   Serial number of failed request:  9
#   Current serial number in output stream:  9

MOUSE_ID=`xinput list | sed -n 's/.*Logitech USB Gaming Mouse.*id=\([0-9]\+\)[^0-9].*/\1/p'`

if [ -z "$MOUSE_ID" ] ; then
  echo 'Logitech Mouse not found'
  exit 1
fi

xinput set-button-map "$MOUSE_ID" 1 2 3 5 4 7 6 2 2

# See also:
# https://github.com/cemmanouilidis/naturalscrolling

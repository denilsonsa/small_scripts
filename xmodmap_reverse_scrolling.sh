#!/bin/sh

# Note that 4,5 and 6,7 are swapped around
xmodmap -e 'pointer = 1 2 3 5 4 7 6 8 9 10 11 12'

# Another solution:
#xinput set-button-map 13 1 2 3 5 4 7 6 8 9 10 11 12
# Where the first number is the id of the device (from "xinput list")

# See also:
# https://github.com/cemmanouilidis/naturalscrolling

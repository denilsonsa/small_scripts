#!/bin/bash
#
# Want to run this script? Search for "Hard-coded" values and replace them
# according to your device.

SCREEN="$1"

if [ -z "$SCREEN" -o "$SCREEN" = "--help" -o "$SCREEN" = "-help" -o "$SCREEN" = "-h" ]; then
	echo 'This script configures a Wacom tablet to one specific monitor, or to '
	echo 'the entire desktop. In addition, it also reduces the tablet area in '
	echo 'order to keep the same aspect ratio as the monitor.'
	echo
	echo 'How to run this script? Run one of the following lines:'
	CONNECTED_DISPLAYS=`xrandr -q --current | sed -n 's/^\([^ ]\+\) connected .*/\1/p'`
	for d in desktop $CONNECTED_DISPLAYS; do
		echo "  $0 $d"
	done
	exit
fi

if [ "$SCREEN" = "desktop" ]; then
	# Sample xrandr line:
	# Screen 0: minimum 320 x 200, current 3286 x 1080, maximum 32767 x 32767

	LINE=`xrandr -q --current | sed -n 's/^Screen 0:.*, current \([0-9]\+\) x \([0-9]\+\),.*/\1 \2/p'`
	read WIDTH HEIGHT <<< "$LINE"
else
	# Sample xrandr lines:
	# LVDS1 connected 1366x768+0+312 (normal left inverted right x axis y axis) 309mm x 174mm
	# VGA1 disconnected (normal left inverted right x axis y axis)
	# HDMI1 connected 1920x1080+1366+0 (normal left inverted right x axis y axis) 509mm x 286mm

	LINE=`xrandr -q --current | sed -n "s/^${SCREEN}"' connected \([0-9]\+\)x\([0-9]\+\)+.*/\1 \2/p'`
	read WIDTH HEIGHT <<< "$LINE"
fi

if [ -z "$WIDTH" -o -z "$HEIGHT" ]; then
	echo "Aborting."
	exit 1
fi

# Hard-coded values for my device.
AREAX=16704
AREAY=12064

# New values respecint aspect ratio:
RATIOAREAY=$(( AREAX * HEIGHT / WIDTH ))
RATIOAREAX=$(( AREAY * WIDTH / HEIGHT ))

if [ "$AREAY" -gt "$RATIOAREAY" ]; then
	NEWAREAX="$AREAX"
	NEWAREAY="$RATIOAREAY"
else
	NEWAREAX="$RATIOAREAX"
	NEWAREAY="$AREAY"
fi

# Hard-coded tablet name.
xsetwacom --set 'Wacom Graphire4 6x8 stylus' Area 0 0 "$NEWAREAX" "$NEWAREAY"
xsetwacom --set 'Wacom Graphire4 6x8 stylus' MapToOutput "$SCREEN"


# $ xsetwacom --list devices
# Wacom Graphire4 6x8 stylus      	id: 9	type: STYLUS
# Wacom Graphire4 6x8 eraser      	id: 10	type: ERASER
# Wacom Graphire4 6x8 cursor      	id: 11	type: CURSOR
# Wacom Graphire4 6x8 pad         	id: 12	type: PAD

# Button mappings only apply to the "pad" device.
# The wheel on Graphire4 acts as mouse buttons 4 and 5 (as a mouse wheel)
# The buttons on Graphire4 act as mouse buttons 8 and 9

# Default Area: 0 0 16704 12064
# ResetArea
#
# Other potentially useful parameters:
# * Mode: absolute or relative
# * Rotate: none, cw, ccw, half
# * MapToOutput: "next" (but is buggy), "desktop", or a name from xrandr

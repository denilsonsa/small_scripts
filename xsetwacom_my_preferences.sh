#!/bin/bash
#
# CONFIGURATION

# Set this to your (stylus) device. Find it by running:
# xsetwacom --list devices
DEVICE='Wacom Graphire4 6x8 Pen stylus'

# These numbers are specific for each device. Get them by running:
# xsetwacom --set "Your device name here" ResetArea
# xsetwacom --get "Your device name here" Area
# TODO: Auto-detect this. Probably.
AREAX=16704
AREAY=12064

# TODO: Make this divisor configurable by command-line:
#  * Either as raw divisor
#  * Or as a function of one display
#
# Let me explain the second case...
# As a user, I want that one full width of my tablet maps to one full width of my second display (or the full desktop). (or height instead of width)
# This means several configurable parameters:
#  - full, half, whatever fraction or multiplier
#  - width or height
#  - which display
# I'll keep this idea noted here for the future.
DIVISOR=6
RELATIVEAREAX="$(( AREAX / DIVISOR ))"
RELATIVEAREAY="$(( AREAY / DIVISOR ))"

# TODO: Rewrite this in a more powerful language (Python!)
# That would make the code a bit cleaner and easier to maintain.
# It would also allow for better argument parsing, and allow for use of three possible styles of MapToOutput:
#  * The screen name (the current method, should work on most systems, except nvidia)
#  * HEAD-0 (required for nvidia, see the manpage and see a feedback in my e-mail address)
#  * WxH+X+y (should work everywhere)

# END OF CONFIGURATION


echo_run() {
	echo "$@"
	"$@"
}

SCREEN="$1"

if [ -z "$SCREEN" -o "$SCREEN" = "--help" -o "$SCREEN" = "-help" -o "$SCREEN" = "-h" ]; then
	echo 'This script configures a Wacom tablet to one specific monitor, or to '
	echo 'the entire desktop. In addition, it also reduces the tablet area in '
	echo 'order to keep the same aspect ratio as the monitor.'
	echo
	echo 'How to run this script? Run one of the following lines:'
	CONNECTED_DISPLAYS=`xrandr -q --current | sed -n 's/^\([^ ]\+\) connected .*/\1/p'`
	for d in relative desktop $CONNECTED_DISPLAYS; do
		echo "  $0 $d"
	done
	exit
fi

if [ "$SCREEN" = "relative" ]; then
	WIDTH="$AREAX"
	HEIGHT="$AREAY"
	SCREEN="${RELATIVEAREAX}x${RELATIVEAREAY}+0+0"
	MODE="relative"
elif [ "$SCREEN" = "desktop" ]; then
	# Sample xrandr line:
	# Screen 0: minimum 320 x 200, current 3286 x 1080, maximum 32767 x 32767

	LINE=`xrandr -q --current | sed -n 's/^Screen 0:.*, current \([0-9]\+\) x \([0-9]\+\),.*/\1 \2/p'`
	read WIDTH HEIGHT <<< "$LINE"
	MODE="absolute"
else
	# Sample xrandr lines:
	# LVDS1 connected 1366x768+0+312 (normal left inverted right x axis y axis) 309mm x 174mm
	# VGA1 disconnected (normal left inverted right x axis y axis)
	# HDMI1 connected 1920x1080+1366+0 (normal left inverted right x axis y axis) 509mm x 286mm

	LINE=`xrandr -q --current | sed -n "s/^${SCREEN}"' connected\( primary\)\? \([0-9]\+\)x\([0-9]\+\)+.*/\2 \3/p'`
	read WIDTH HEIGHT <<< "$LINE"
	MODE="absolute"
fi

if [ -z "$WIDTH" -o -z "$HEIGHT" ]; then
	echo "Aborting."
	exit 1
fi

# New values respecing aspect ratio:
RATIOAREAY=$(( AREAX * HEIGHT / WIDTH ))
RATIOAREAX=$(( AREAY * WIDTH / HEIGHT ))

if [ "$AREAY" -gt "$RATIOAREAY" ]; then
	NEWAREAX="$AREAX"
	NEWAREAY="$RATIOAREAY"
else
	NEWAREAX="$RATIOAREAX"
	NEWAREAY="$AREAY"
fi

if [ -z "$(xsetwacom --list devices)" ] ; then
	true
	#echo 'No devices found.'
else
	echo_run xsetwacom --set "$DEVICE" Area 0 0 "$NEWAREAX" "$NEWAREAY"
	echo_run xsetwacom --set "$DEVICE" Mode "$MODE"
	echo_run xsetwacom --set "$DEVICE" MapToOutput "$SCREEN"
fi

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
#
# Other potentially useful tool:
# * https://gitlab.freedesktop.org/xorg/app/xinput/-/issues/9
# * xinput map-to-output ...
# * xinput set-prop ... 'Coordinate Transformation Matrix' ...

# See also:
# * https://wiki.archlinux.org/title/Graphics_tablet
# * https://gist.github.com/tom-galvin/6c19fe907945d735c045

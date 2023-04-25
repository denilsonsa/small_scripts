#!/bin/bash
#
# This script requires: bash, sed, awk
#
# Using sed because not all awk versions support replacing by matched groups from the regex.
# But then it requires a sed version with support for "-u":
# * GNU sed
# * OpenBSD sed
# * FreeBSD sed
# * does NOT work with busybox sed
#
# Works with the following awk implementations:
# * gawk
# * mawk
# * nawk
# * original-awk
# * BusyBoxy awk

SCRIPTNAME=`basename "$0"`

print_help() {
	cat << EOF
Usage: $SCRIPTNAME [-root] [-geometry geom] [-display display]

Uses "xev" to display how many pixels the mouse pointer has moved after each
motion event. Useful to fine-tune your pointer speed/acceleration settings.
Also useful to measure the quality or resolution of your mouse.

See also:
* xinput and xinput-gui
* mouse-dpi-tool
* man 4 libinput
* https://wayland.freedesktop.org/libinput/doc/latest/configuration.html#pointer-acceleration
* https://wayland.freedesktop.org/libinput/doc/latest/pointer-acceleration.html#pointer-acceleration
* https://gitlab.freedesktop.org/libevdev/libevdev/-/blob/master/tools/mouse-dpi-tool.c
EOF
}

# parse_parameters:
while [[ "$1" == -* ]] ; do
	case "$1" in
		-h|-help|--help)
			print_help
			exit
			;;
# For simplicity, any additional parameters are passed directly to xev
#		*)
#			echo "Invalid parameter: '$1'"
#			exit 1
#			;;
	esac
done

# check dependencies
if ! type xev &>/dev/null ; then
	echo "You are missing xev. Please install it."
	exit 1
fi

AWK_BIN="awk"
AWK_PARAMS=( )
# Workaround for mawk:
# http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=593504
AWK_VERSION="$(echo | "${AWK_BIN}" -W version 2>&1)"
if [[ "${AWK_VERSION}" == mawk* ]] ; then
	AWK_PARAMS+=(-W interactive)
fi

# xev: only mouse events, one event per line, on the root window.
# sed: unbuffered, only print matching lines.
xev -event mouse -1 "$@" \
	| sed -u -n 's/MotionNotify.* (\([0-9]*\),\([0-9]*\)), root:(\([0-9]*\),\([0-9]*\)).*/\1 \2 \3 \4/p' \
	| "${AWK_BIN}" "${AWK_PARAMS[@]}" '
function abs(n) {
	if (n < 0) {
		return -n
	}
	return n
}

function sign(n) {
	if (n < 0) {
		return -1
	} else if (n > 0) {
		return 1
	}
	return 0
}

# i is a local variable.
function blockbar(n, i) {
	s = ""
	for ( i=0 ; i < 8 && n > 0 ; i++ ) {
		r = n - 1
		if (r >= BLOCK_LEN) {
			r = BLOCK_LEN - 1
		}
		n -= BLOCK_LEN
		s = s BLOCK[r]
	}
	return s
}

BEGIN {
	ARROW[0] = "↖"
	ARROW[1] = "↑"
	ARROW[2] = "↗"
	ARROW[3] = "←"
	ARROW[4] = "·"
	ARROW[5] = "→"
	ARROW[6] = "↙"
	ARROW[7] = "↓"
	ARROW[8] = "↘"

	BLOCK[0] = "⠂"
	BLOCK[1] = "⠒"
	BLOCK_LEN = 2
}
{
	if (has_prev) {
		# Local, window-based delta.
		dx = $1 - prev_x
		dy = $2 - prev_y
		# Global, root-window-based delta.
		rx = $3 - root_x
		ry = $4 - root_y

		# Euclidean distance.
		dist = sqrt(dx * dx + dy * dy)
		# Manhattan distance.
		xy = abs(dx) + abs(dy)

		printf("delta:%+6d,%+6d", dx, dy)
		printf("  pos:%5d,%5d", $3, $4)
		if (dx != rx || dy != ry) {
			# Somehow, the distance between the window-based pointer position
			# and the root window pointer position diverged.
			printf("  (%+6d,%+6d)", rx, ry)
		}

		printf("  dist:%7.1f", dist)
		printf("  |x|+|y|:%5d", xy)

		printf("  %s %s", ARROW[1 + sign(dx) + 3 * (1 + sign(dy))], blockbar(xy))

		printf("\n")
	}

	prev_x = $1
	prev_y = $2
	root_x = $3
	root_y = $4
	has_prev = 1

	# Flush after every line for better UX.
	fflush()
}
'

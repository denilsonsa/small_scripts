#!/bin/bash

SCRIPTFILENAME=`basename "$0"`
SCRIPTNAME="$SCRIPTFILENAME version 1.0"

# URL to PuckMan (Japan set 1, Probably Bootleg)
#URL="http://www.planetemu.net/index.php?section=roms&dat=414&action=showrom&id=585031"

# URL to Sonic The Hedgehog (U) (V1.1) [!] for Game Gear
URL="http://www.planetemu.net/index.php?section=roms&dat=609&action=showrom&id=767925"


print_help() {
	echo "$SCRIPTNAME"
	echo "Usage: $SCRIPTFILENAME [-v] <extraseconds> [URL]"
	echo "This script waits (using sleep) the time needed before a new download on"
	echo "planetemu site."
	echo ""
	echo "This script will download the URL (an internal one or the one passed as"
	echo "parameter) and read how many seconds it must wait before a new download. Then"
	echo "the script will sleep this number of seconds plus extraseconds."
	echo ""
	echo "If -v is the first option, then the script will print the time it will wait,"
	echo "just before falling asleep."
	echo ""
	echo "This script is not affiliated in any way with Planet Emulation site."
#	echo ".............................................................................."
}

VERBOSE=0
if [ "$1" == "-v" ]; then
	VERBOSE=1;
	shift
fi

if [ -n "$1" ] && (( $1 >= 0 )); then
	extraseconds="$1"
	if [ -n "$2" ]; then
		URL="$2"
	fi
	seconds=`wget -U Mozilla/4.0 -q -O - "$URL" | sed -n '/var restant/ { ; s/^[ \t]*var restant *= *\([0-9]\+\) *;.*$/\1/p ; q ; }'`
	totalseconds=$(( seconds + extraseconds ))
	[ "$VERBOSE" == 1 ] && echo "Waiting $seconds + $extraseconds seconds..."
	sleep $totalseconds
else
	print_help
fi

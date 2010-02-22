#!/bin/bash

MYNAME=`basename "$0"`

print_help() {
	cat << EOF
Usage: $MYNAME file [ files... ]

This script will call pngcrush to remove gAMA chunk from PNG files, in order
to make them work well inside Internet Explorer.

In addition, other color-related chunks are removed as well.
EOF
}


if [  -z "$1"  -o  "$1" = "-h"  -o  "$1" = "--help"  ] ; then
	print_help
	exit 1
fi

for i in "$@" ; do
	TMPFILE=`mktemp`
	pngcrush -rem cHRM -rem gAMA -rem iCCP -rem sRGB "$i" "$TMPFILE"
	# Damn pngcrush that does not correctly return an useful exit code
	# -s FILE        True if file exists and is not empty.
	if [ -s "$TMPFILE" ] ; then
		cat "$TMPFILE" > "$i"
	fi
	rm -f "$TMPFILE"
done

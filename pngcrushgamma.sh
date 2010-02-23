#!/bin/sh

MYNAME=`basename "$0"`

print_help() {
	cat << EOF
Usage: $MYNAME [-v] file [ files... ]

This script will call pngcrush to remove gAMA chunk from PNG files, so that
they will look fine inside Internet Explorer.

In addition, other color-related chunks are also removed: cHRM, iCCP, sRGB

Option:
  -v     verbose mode

Read more:
http://morris-photographics.com/photoshop/articles/png-gamma.html
http://snook.ca/archives/design/which_image_for/#c21159
http://www.hanselman.com/blog/GammaCorrectionAndColorCorrectionPNGIsStillTooHard.aspx
EOF
}


if [ -z "$1"  -o  "$1" = "-h"  -o  "$1" = "--help"  ] ; then
	print_help
	exit 1
fi

VERBOSE=0
if [ "$1" = "-v" ] ; then
	VERBOSE=1
	shift
fi


if [ "$VERBOSE" = 1 ] ; then
	PARAM=""
else
	PARAM="-q"
fi

for i in "$@" ; do
	TMPFILE=`mktemp`
	pngcrush $PARAM -rem cHRM -rem gAMA -rem iCCP -rem sRGB "$i" "$TMPFILE"
	# Damn pngcrush that does not correctly return an useful exit code
	# -s FILE        True if file exists and is not empty.
	if [ -s "$TMPFILE" ] ; then
		echo "Updated file '$i'."
		cat "$TMPFILE" > "$i"
	else
		echo "File '$i' was not changed."
	fi
	rm -f "$TMPFILE"
done

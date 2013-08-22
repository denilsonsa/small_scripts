#!/bin/bash

BASENAME="$(basename "$0")"

# Help.
if [ "$1" = '--help' -o  "$1" = '-help' -o  "$1" = '-h' ]; then
	echo "Usage: ${BASENAME} [-t FRONT_COVER] front.jpg file1.mp3 file2.mp3 ..."
	echo ""
	echo "It will remove any embedded pictures from the MP3 files and add the specified picture to the MP3 files."
	echo "The picture type will be auto-detected from the filename (ignoring case):"
	echo "  AlbumArt* -> 03 FONT_COVER"
	echo "  cover*    -> 03 FONT_COVER"
	echo "  front*    -> 03 FONT_COVER"
	echo "  back*     -> 04 BACK_COVER"
	echo "  booklet*  -> 05 LEAFLET"
	echo "  leaflet*  -> 05 LEAFLET"
	echo "  media*    -> 06 MEDIA"
	echo "  medium*   -> 06 MEDIA"
	echo "  *         -> 00 OTHER"
	exit
fi

# Picture type, and -t/--type command-line flag.
TYPE=""
if [ "$1" = '-t' -o "$1" = '--type' ]; then
	shift
	TYPE="$1"
	if [ -z "${TYPE}" ]; then
		echo "The '-t' option requires a parameter. Aborting."
		exit 2
	fi
	shift
fi

# The path to the embedded picture.
PICTURE="$1"
shift
if [ ! -r "${PICTURE}" ]; then
	echo "Picture '${PICTURE}' was not found or is not readable. Aborting."
	exit 1
fi

# Auto-detect type.
# http://stackoverflow.com/questions/2264428/converting-string-to-lower-case-in-bash-shell-scripting
AUTO_TYPE="OTHER"
case "${PICTURE,,}" in
	albumart* | cover* | front* )
		AUTO_TYPE="FRONT_COVER"
		;;
	back* )
		AUTO_TYPE="BACK_COVER"
		;;
	booklet* | leaflet* )
		AUTO_TYPE="LEAFLET"
		;;
	media* | medium* )
		AUTO_TYPE="MEDIA"
		;;
esac
if [ -z "${TYPE}" ]; then
	TYPE="${AUTO_TYPE}"
fi

# The MP3 files.
if [ -z "$1" ]; then
	echo "Missing parameters: MP3 files to be modified. Aborting."
	exit 1
fi

# I can use a single command because eyeD3 first removes tags, and then
# edits/adds tags.
# Optional flags: --to-v2.4
# TSO2 frame is not supported by eyeD3, and it is not essential anyway.
# It will also change TSOP to XSOP.
set -x
eyeD3 --remove-frame TSO2 \
	--remove-all-images --add-image "${PICTURE}:${TYPE}" \
	"$@"

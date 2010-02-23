#!/bin/bash

SCRIPTNAME=`basename "$0"`

print_help() {
	cat << EOF
Usage: $SCRIPTNAME [-tc|-tg|-td] [-p|-v] format files [files...]
Renames files to "format", using Exif timestamps.
"format" is a string that will be passed to strftime.
"mv -i" will be used to rename files, so no overwriting is done without user confirmation.

Options:
  -tc   Use "image created" timestamp
  -tg   Use "image generated" timestamp (default)
  -td   Use "image digitized" timestamp
  -p    Pretend, print the mv commands, but do not execute them
  -v    Verbose, print the mv commands before executing them
  --    Marks the end of options; the parameter next to it is considered a file

Example:
  $SCRIPTNAME 'MyPhotos-%F_%H-%M-%S.jpg' *.jpg
    This will rename files to MyPhotos-YYYY-MM-DD_HH-MM-SS.jpg

Note: this script does not handle duplicate filenames.
EOF
}



# BEGIN

WHICH_TIME="-tg"
PRETEND="0"
VERBOSE="0"


# parse_parameters:
while [[ "$1" == -* ]] ; do
	case "$1" in
		-tc)
			WHICH_TIME="-tc"
			shift
			;;
		-tg)
			WHICH_TIME="-tg"
			shift
			;;
		-td)
			WHICH_TIME="-td"
			shift
			;;
		-p)
			PRETEND="1"
			shift
			;;
		-v)
			VERBOSE="1"
			shift
			;;
		-h|-help|--help)
			print_help
			exit
			;;
		--)
			#echo "-- found"
			shift
			break
			;;
		*)
			echo "Invalid parameter: '$1'"
			exit 1
			;;
	esac
done

if [ "$#" -lt 2 ] ; then
	print_help
	exit 1
fi

FORMAT="$1"
shift

for f in "$@" ; do
	TIMESTAMP=`exiftime $WHICH_TIME "$f" | sed -n 's/[^0-9]*: \+\([0-9: ]\+\)/\1/p' | sed 's/:/ /g'`
	if echo "$TIMESTAMP" | egrep -q '^[0-9]+( [0-9]+){5} *$' ; then
		NEWFILENAME=`awk 'BEGIN{t=mktime("'"$TIMESTAMP"'"); print strftime("'"$FORMAT"'",t)}'`
		if [[ ( "$PRETEND" == 1 ) || ( "$VERBOSE" == 1 ) ]] ; then
			echo mv -i "$f" "$NEWFILENAME"
		fi
		if [[ "$PRETEND" == 0 ]] ; then
			mv -i "$f" "$NEWFILENAME"
		fi
	else
		echo "Error finding time for $f"
	fi
done

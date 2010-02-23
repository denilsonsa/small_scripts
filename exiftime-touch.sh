#!/bin/bash

SCRIPTNAME=`basename "$0"`

print_help() {
	cat << EOF
Usage: $SCRIPTNAME [-tc|-tg|-td] [-p|-v] files [files...]
Touch the files, setting their modified time to the Exif timestamps.

Options:
  -tc   Use "image created" timestamp
  -tg   Use "image generated" timestamp (default)
  -td   Use "image digitized" timestamp
  -p    Pretend, print the touch commands, but do not execute them
  -v    Verbose, print the touch commands before executing them
  --    Marks the end of options; the parameter next to it is considered a file
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

if [ "$#" -lt 1 ] ; then
	print_help
	exit 1
fi

for f in "$@" ; do
	TIMESTAMP=`exiftime $WHICH_TIME "$f" | sed -n 's/[^0-9]*: \+\([0-9: ]\+\)/\1/p' | sed 's/:/ /g'`
	if echo "$TIMESTAMP" | egrep -q '^[0-9]+( [0-9]+){5} *$' ; then
		TOUCHTIME=`echo "$TIMESTAMP" | sed 's/ //g; s/\([0-9]\{2\}\)$/.\1/'`
		if [[ ( "$PRETEND" == 1 ) || ( "$VERBOSE" == 1 ) ]] ; then
			echo touch -t "$TOUCHTIME" "$f"
		fi
		if [[ "$PRETEND" == 0 ]] ; then
			touch -t "$TOUCHTIME" "$f"
		fi
	else
		echo "Error finding time for $f"
	fi
done

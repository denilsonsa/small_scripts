#/bin/bash

SCRIPTFILENAME=`basename "$0"`
SCRIPTNAME="$SCRIPTFILENAME version 1.0"

print_help() {
	echo "$SCRIPTNAME"
	echo "Usage: $SCRIPTFILENAME <URL> [URL ...]"
	echo "This script will parse a ROM listing page from planetemu site and"
	echo "print all ROMs on that page, with the following format:"
	echo "<dat-id> <TAB> <rom-id> <TAB> <rom-size> <TAB> <rom-name>"
	echo ""
	echo "This script is not affiliated in any way with Planet Emulation site."
#	echo ".............................................................................."
}

if [ "$#" = 0 ]; then
	print_help
else
	while [ -n "$1" ]; do
		URL="$1"
		#wget -U Mozilla/4.0 -q -O - "$URL" | sed -n '/href.*action=showrom/ { ; s/^.*href=.*&dat=\([0-9]\+\).*&id=\([0-9]\+\)[^>]*>\([^<]\+\)<\/a>.*$/\1\t\2\t\3/p }'
		#wget -U Mozilla/4.0 -q -O - "$URL" | sed -n '/href.*action=showrom/ { ; s/^.*href=.*&amp;dat=\([0-9]\+\).*&amp;id=\([0-9]\+\)[^>]*>\([^<]\+\)<\/a>.*$/\1\t\2\t\3/p }'
		wget -U Mozilla/4.0 -q -O - "$URL" | sed -n '/href.*action=showrom/ { ; s/^.*href=.*&amp;dat=\([0-9]\+\).*&amp;id=\([0-9]\+\)[^>]*>\([^<]\+\)<\/a>.*taillerom" nowrap>&nbsp;\([0-9. KMo]\+\)&nbsp;.*$/\1\t\2\t\4\t\3/p }'
		shift
	done
fi

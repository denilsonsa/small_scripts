#/bin/bash

SCRIPTFILENAME=`basename "$0"`
SCRIPTNAME="$SCRIPTFILENAME version 1.0"

print_help() {
	echo "$SCRIPTNAME"
	echo "Usage: $SCRIPTFILENAME <dat-id> <rom-id>"
	echo "This script prints what should be the filename for a given rom-id inside"
	echo "planetemu rom collection."
	echo ""
	echo "In fact, only the rom-id is needed, but this script still requires the dat-id"
	echo "to avoid sending invalid dat-id to planetemu site."
	echo ""
	echo "This script is not affiliated in any way with Planet Emulation site."
#	echo ".............................................................................."
}

if [ "$#" != 2 ]; then
	print_help
else
	DAT="$1"
	ID="$2"
	URL="http://www.planetemu.net/index.php?section=roms&dat=${DAT}&action=showrom&id=${ID}"
	wget -U Mozilla/4.0 -q -O - "$URL" | sed -n '/<td.*>Archive<\/td>/ { ; n ; s/^.*<td[^>]*>\(.*\)<\/td>.*$/\1/p ; q }'
fi

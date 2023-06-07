#!/bin/bash
# A wrapper around "disper" tool.
# http://willem.engen.nl/projects/disper/

STATE_FILE="$HOME"/.disper-toggle.state
#STATE_FILE=/var/run/disper-toggle.state

# On my laptop, this is added to the /var/log/messages when I press
# the LCD/CRT button (Fn+F8):
#   ACPI event unhandled: video/switchmode VMOD 00000080 00000000
#   ACPI event unhandled: hotkey ATK0100:00 00000061 00000008
#
# So, I've added the file
#   /etc/acpi/events/my-laptop-video-button
# with these contents:
#   event=video/switchmode VMOD 00000080 00000000
#   action=/usr/local/bin/disper-toggle.sh
#
# huh... does not work
# If someone has some help, it is appreciated!
# http://forums.gentoo.org/viewtopic-t-859737.html


############################################################
# Don't edit below this line

TOTAL_STATES=3

SCRIPT_NAME=`basename "$0"`


print_help() {
	echo "Usage: ${SCRIPT_NAME} [state]"
	echo "With no parameters, it just changes to the next state."
	echo "With a single number parameter (from 0 to $(( $TOTAL_STATES -1 )), switch to that state."
	echo "The next state is saved at '$STATE_FILE'."
}

if [[ "$#" -gt 1 ]] ; then
	echo "Too many parameters"
	print_help
	exit 1
elif [[ "$#" == 1  &&  "$1" != $(( "$1" )) ]] ; then
	#echo "The first parameter is not a number"
	print_help
	exit 1
fi

# Loading state
STATE=$(( `cat "$STATE_FILE" 2> /dev/null` ))
NEW_STATE=$(( ($STATE +1 ) % $TOTAL_STATES ))

# Saving new state
echo "$NEW_STATE" > "$STATE_FILE"

case "$STATE" in
	0)
		echo "${SCRIPT_NAME}: Enabling the second display"
		disper -S
		;;
	1)
		echo "${SCRIPT_NAME}: Cloning the second display"
		disper -c
		;;
	2)
		echo "${SCRIPT_NAME}: Enabling the primary display"
		disper -s
		;;
esac


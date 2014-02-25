#!/bin/sh

# Toggles my touchpad on ASUS X450C notebook.
# Yes, the touchpad name is hard-coded.

DEVICE='ETPS/2 Elantech Touchpad'
STATE="$(xinput list-props "${DEVICE}" | sed -n 's/^[ \t]*Device Enabled ([0-9]*):[ \t]*\([0-1]\)[ \t]*$/\1/p' )"

if [ "${STATE}" = 1 ] ; then
	xinput disable "${DEVICE}"
else
	xinput enable "${DEVICE}"
fi

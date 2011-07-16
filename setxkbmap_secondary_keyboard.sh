#!/bin/sh

# Linux rocks!
# http://superuser.com/questions/75817/two-keyboards-on-one-computer-when-i-write-with-a-i-want-a-us-keyboard-layout-w
#
# Too bad about Windows:
# http://superuser.com/questions/177305/using-multiple-keyboards-with-different-keyboard-layouts-in-windows


echo_run() {
	echo "$@"
	"$@"
}

# Finding the id from this line:
#     ↳ Microsoft Microsoft® 2.4GHz Transceiver v8.0      id=14   [slave  keyboard (3)]

KBD_ID=`xinput -list | sed -n 's/^.*Microsoft.*2\.4GHz Transceiver.*id=\([0-9]\+\).*slave \+keyboard.*$/\1/p'`

if [ -n "$KBD_ID" ] ; then
	echo_run setxkbmap -device "$KBD_ID" br abnt2 altwin:super_win numpad:windows
fi

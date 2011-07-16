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
	echo_run setxkbmap -device "$KBD_ID" br abnt2 numpad:microsoft
fi


# Configuring xorg.conf to automatically set the keyboard layout for this device:
#
# First, we need to find the Vendor and the Product from the device:
# /sbin/udevadm info --query=all --name=/dev/input/by-id/usb-Microsoft_Microsoft®_2.4GHz_Transceiver_v8.0-event-kbd
#
# Source:
#  https://bbs.archlinux.org/viewtopic.php?id=96422
#
#
# Then we must add this code to xorg.conf (for xorg-server-1.8):
#
# Section "InputClass"
#         Identifier "keyboard-microsoft-wireless"
#         Driver "evdev"
#         Option "XkbLayout" "br"
#         Option "XkbVariant" "abnt2"
#         Option "XkbOptions" "numpad:microsoft"
#
#         MatchIsKeyboard "on"
#
#         # The following rules apply substring matching:
#         MatchVendor "Microsoft"
#         MatchProduct "2.4GHz Transceiver"
# EndSection
#
# Source:
#  http://www.gentoo.org/proj/en/desktop/x/x11/xorg-server-1.8-upgrade-guide.xml

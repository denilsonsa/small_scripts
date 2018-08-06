#!/bin/sh

echo_run() {
	echo "$@"
	"$@"
}

# new full-speed USB device number 98 using xhci_hcd
# New USB device found, idVendor=05ac, idProduct=026c
# New USB device strings: Mfr=1, Product=2, SerialNumber=3
# Product: Magic Keyboard with Numeric Keypad
# Manufacturer: Apple Inc.
#
# hid-generic: USB HID v1.10 Device [Apple Inc. Magic Keyboard with Numeric Keypad]

# Finding the id from this line:
#     ↳ Apple Inc. Magic Keyboard with Numeric Keypad	id=11	[slave  keyboard (3)]

KBD_ID=`xinput --list | sed -n 's/^.* Apple Inc\. Magic Keyboard with Numeric Keypad.*id=\([0-9]\+\)[ \t].*slave \+keyboard.*$/\1/p'`

if [ -n "$KBD_ID" ] ; then
	# https://unix.stackexchange.com/q/86933
	# First to clear the previously set options
	echo_run setxkbmap -device "$KBD_ID" -option
	# Then to set the options. (man xkeyboard-config)
	# * Capslock is another backspace.
	# * Bottom-left modifiers are: Ctrl, Super, Alt
	# * Bottom-right modifiers are: AltGr, Compose, Ctrl
	# * F13, F14, F15 are PrtScn/SysRq, Scroll Lock, Pause/Break
	echo_run setxkbmap -device "$KBD_ID" us altgr-intl caps:backspace numpad:microsoft altwin:swap_alt_win apple:alupckeys lv3:rwin_switch compose:ralt
	# fn is in place of the usual Insert key.
	# Thus, remapping Eject to Insert
	xmodmap -e 'keysym XF86Eject = Insert NoSymbol Insert'
fi

#!/bin/sh

echo_run() {
	echo "$@"
	"$@"
}

# Useful layout+variant combinations:
# br abnt2
# us intl
# us altgr-intl

#echo_run setxkbmap us altgr-intl caps:escape compose:menu numpad:microsoft
echo_run setxkbmap -option
echo_run setxkbmap us altgr-intl caps:backspace compose:menu numpad:microsoft

#!/bin/bash
# META:ICON = "display"
#
# Further reading:
#
# * https://askubuntu.com/questions/371261/display-monitor-info-via-command-line
# * https://unix.stackexchange.com/questions/67983/get-monitor-make-and-model-and-other-info-in-human-readable-form
# * https://stackoverflow.com/questions/10500521/linux-retrieve-monitor-names
# * https://github.com/MestreLion/scripts/blob/master/monitor-switch
# * https://en.wikipedia.org/wiki/Extended_Display_Identification_Data
# * apt-get install read-edid:
#     * http://polypux.org/projects/read-edid/
# * apt-get install edid-decode:
#     * https://cgit.freedesktop.org/xorg/app/edid-decode
# * /sys/class/drm/card*-*/edid
# * xrandr --prop


# Input: xrandr --prop
# Output:
# LVDS-1 connected 00ffffffffffff004ca349360000000000150103801f11780a09e59757548a27225054000000010101010101010101010101010101017d1e5618510016303020250035ae100000190000000f0000000000000000001ec8066a00000000fe0053414d53554e470a2020202020000000fe004c544e313430415432305030310021
# DP-1 disconnected
# HDMI-1 connected 00ffffffffffff0005e35123b00500002317010380331d782a77c5a3544f9f27115054bfef00d1c0b30095008180814081c001010101023a801871382d40582c4500fd1e1100001e000000fd00324c1e5311000a202020202020000000fc00323335310a2020202020202020000000ff0032333033384941303031343536016b02031ef14b0514101f04130312021101230907018301000065030c0010008c0ad08a20e02d10103e9600fd1e11000018011d007251d01e206e285500fd1e1100001e8c0ad08a20e02d10103e9600fd1e110000188c0ad090204031200c405500fd1e110000180000000000000000000000000000000000000000000000000083
# VGA-1 disconnected
extract_edids_from_xrandr_input() {
	# Adds an empty line at the end of the input.
	{ cat ; echo ; } | sed -n '
		# Printing and clearing the hold space.
		/^\([^ \t]\|$\)/ {
			x
			/.\+/ {
				s/\n\+//g
				s/ \+$//
				p
			}
			s/.*//
			x
		}

		# Start of each display/connection.
		/^[^ \t].*\(dis\)\?connected/ {
			s/^\([^ \t]\+\) \+\(\(dis\)\?connected\) .*/\1 \2 /
			h
		}

		# EDID section.
		/^[ \t]\+EDID:/,/\(:\|[^ \t][ \t]\+[^ \t]\)/ {
			/^[ \t]\+[0-9a-fA-F]\+[ \t]*$/ {
				s/[ \t]\+//g
				H
			}
		}
	'
}


# Input: the output of extract_edids_from_xrandr_input
# Output:
# LVDS-1 connected 4ca34936000000000015
# DP-1 disconnected
# HDMI-1 connected 05e35123b00500002317
# VGA-1 disconnected
replace_edid_with_serial() {
	# Extracting the serial number from the full EDID.
	sed 's/ 00FFFFFFFFFFFF00\([0-9a-fA-F]\{20\}\)[0-9a-fA-F]\+/ \1/i'
}

# Input: the output of replace_edid_with_serial
# Output (sorted and upper-case):
# LVDS-1 4CA34936000000000015
# HDMI-1 05E35123B00500002317
extract_only_connected() {
	tr '[a-z]' '[A-Z]' | sed -n '
		s/^\([^ ]\+\) CONNECTED \([0-9A-Z]\+\)$/\1 \2/p
	' | sort
}


export LC_ALL=C

status="$(
xrandr --prop \
	| extract_edids_from_xrandr_input \
	| replace_edid_with_serial \
	| extract_only_connected
)"

nl=$'\n'
laptop='4CA34936000000000015'
aoc2351a='05E35123B00500002317'
aoc2351b='05E3752401010101171A'
asusM51Sn='0ED403001E2000003312'
philips='410C0100010101010110'

case "${status}" in
	"LVDS-1 ${laptop}")
		~/.screenlayout/video-only-laptop.sh
		;;
	"LVDS-1 ${laptop}${nl}HDMI-1 ${aoc2351a}") ;&
	"LVDS-1 ${laptop}${nl}HDMI-1 ${aoc2351b}")
		#~/.screenlayout/video-1080p-at-right.sh
		#~/.screenlayout/video-1080p-vertical-at-right.sh
		#~/.screenlayout/video-1080p-vertical-at-left.sh
		;;
	"LVDS-1 ${laptop}${nl}HDMI-1 ${asusM51Sn}")
		~/.screenlayout/video-asusM51Sn-at-right.sh
		;;
	"LVDS-1 ${laptop}${nl}HDMI-1 ${philips}")
		#~/.screenlayout/video-1080i-at-top.sh
		~/.screenlayout/video-720p-at-top.sh
		;;
	*)
		echo 'Unknown configuration:'
		echo "${status}"
		;;
esac

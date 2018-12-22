#!/bin/sh

echo_run() {
	echo "$@"
	"$@"
}

xsp_microsoft() {
	echo_run xinput set-prop 'Microsoft  Microsoft Basic Optical Mouse v2.0 ' "$@"
}
xsp_logitech() {
	echo_run xinput set-prop 'Logitech USB Laser Mouse' "$@"
}
xsp_logitech2() {
	echo_run xinput set-prop 'Logitech M705' "$@"
}
xsp_logitech3() {
	echo_run xinput set-prop 'pointer:Logitech MX Master 2S' "$@"
	echo_run xinput set-prop 'pointer:MX Master 2S' "$@"
}
xsp_dell() {
	echo_run xinput set-prop 'PixArt Dell MS116 USB Optical Mouse' "$@"
}

# Device Accel Profile (259):	0
# Device Accel Constant Deceleration (260):	1.000000
# Device Accel Adaptive Deceleration (261):	1.000000
# Device Accel Velocity Scaling (262):	10.000000

#xsp 'Device Accel Velocity Scaling' 1.0

# https://wiki.archlinux.org/index.php/Mouse_acceleration#Disabling_mouse_acceleration
# http://xorg.freedesktop.org/wiki/Development/Documentation/PointerAcceleration/#accelerationprofileinteger
xsp_microsoft 'Device Accel Profile' -1
xsp_logitech  'Device Accel Profile' -1
xsp_logitech2 'Device Accel Profile' -1
#xsp_logitech3 'Device Accel Profile' -1
# https://jlk.fjfi.cvut.cz/arch/manpages/man/libinput.4
# 2 boolean values (8 bit, 0 or 1), in order "adaptive", "flat"
xsp_microsoft 'libinput Accel Profile Enabled' 0 1
xsp_logitech  'libinput Accel Profile Enabled' 0 1
xsp_logitech2 'libinput Accel Profile Enabled' 0 1
xsp_logitech3 'libinput Accel Profile Enabled' 0 1

# Constant mouse speed:
xsp_microsoft 'Device Accel Constant Deceleration' 1.5



#if device_id=`xinput --list --id-only 'pointer:MX Master 2S'`; then
	#echo_run xinput set-prop "$device_id" 'libinput Accel Profile Enabled' 0 1
	# https://gitlab.freedesktop.org/libinput/libinput/issues/195
	# https://crbug.com/913403
	#echo_run xinput set-prop "$device_id" 'libinput Natural Scrolling Enabled' 1
	# Inverting horizontal scroll buttons: 6 and 7
	# But this has no effect in Chrome. :(
	#echo_run xinput set-button-map "$device_id" 1 2 3 4 5 7 6 8 9 10 11 12 13 14 15 16 17 18 19 20
#fi

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
xsp_logitech 'Device Accel Profile' -1
xsp_logitech2 'Device Accel Profile' -1

# Constant mouse speed:
xsp_microsoft 'Device Accel Constant Deceleration' 1.5

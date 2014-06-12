#!/bin/sh

xsp_microsoft() {
	xinput set-prop 'Microsoft  Microsoft Basic Optical Mouse v2.0 ' "$@"
}
xsp_logitech() {
	xinput set-prop 'Logitech USB Laser Mouse' "$@"
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

# Constant mouse speed:
xsp_microsoft 'Device Accel Constant Deceleration' 1.5

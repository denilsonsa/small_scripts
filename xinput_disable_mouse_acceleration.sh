#!/bin/sh

xsp() {
	xinput set-prop 'Microsoft  Microsoft Basic Optical Mouse v2.0 ' "$@"
}

# Device Accel Profile (259):	0
# Device Accel Constant Deceleration (260):	1.000000
# Device Accel Adaptive Deceleration (261):	1.000000
# Device Accel Velocity Scaling (262):	10.000000

xsp 'Device Accel Velocity Scaling' 1.0

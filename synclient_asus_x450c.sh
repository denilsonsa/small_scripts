#!/bin/sh

# See also: man synaptics

# (II) config/udev: Adding input device ETPS/2 Elantech Touchpad (/dev/input/event9)
# (**) ETPS/2 Elantech Touchpad: Applying InputClass "evdev touchpad catchall"
# (**) ETPS/2 Elantech Touchpad: Applying InputClass "touchpad catchall"
# (**) ETPS/2 Elantech Touchpad: Applying InputClass "Default clickpad buttons"
# (II) LoadModule: "synaptics"
# (II) Loading /usr/lib/xorg/modules/input/synaptics_drv.so
# (II) Module synaptics: vendor="X.Org Foundation"
# 	compiled for 1.14.2, module version = 1.7.1
# 	Module class: X.Org XInput Driver
# 	ABI class: X.Org XInput driver, version 19.1
# (II) Using input driver 'synaptics' for 'ETPS/2 Elantech Touchpad'
# (**) ETPS/2 Elantech Touchpad: always reports core events
# (**) Option "Device" "/dev/input/event9"
# (II) synaptics: ETPS/2 Elantech Touchpad: found clickpad property
# (--) synaptics: ETPS/2 Elantech Touchpad: x-axis range 0 - 3260 (res 32)
# (--) synaptics: ETPS/2 Elantech Touchpad: y-axis range 0 - 1793 (res 32)
# (--) synaptics: ETPS/2 Elantech Touchpad: pressure range 0 - 255
# (--) synaptics: ETPS/2 Elantech Touchpad: finger width range 0 - 15
# (--) synaptics: ETPS/2 Elantech Touchpad: buttons: left double triple
# (--) synaptics: ETPS/2 Elantech Touchpad: Vendor 0x2 Product 0xe
# (**) Option "SoftButtonAreas" "50% 0 82% 0 0 0 0 0"
# (--) synaptics: ETPS/2 Elantech Touchpad: touchpad found
# (**) ETPS/2 Elantech Touchpad: always reports core events
# (**) Option "config_info" "udev:/sys/devices/platform/i8042/serio4/input/input9/event9"
# (II) XINPUT: Adding extended input device "ETPS/2 Elantech Touchpad" (type: TOUCHPAD, id 12)
# (**) synaptics: ETPS/2 Elantech Touchpad: (accel) MinSpeed is now constant deceleration 2.5
# (**) synaptics: ETPS/2 Elantech Touchpad: (accel) MaxSpeed is now 1.75
# (**) synaptics: ETPS/2 Elantech Touchpad: (accel) AccelFactor is now 0.054
# (**) ETPS/2 Elantech Touchpad: (accel) keeping acceleration scheme 1
# (**) ETPS/2 Elantech Touchpad: (accel) acceleration profile 1
# (**) ETPS/2 Elantech Touchpad: (accel) acceleration factor: 2.000
# (**) ETPS/2 Elantech Touchpad: (accel) acceleration threshold: 4
# (--) synaptics: ETPS/2 Elantech Touchpad: touchpad found
# (II) config/udev: Adding input device ETPS/2 Elantech Touchpad (/dev/input/mouse0)
# (**) ETPS/2 Elantech Touchpad: Ignoring device from InputClass "touchpad ignore duplicates"

alias xsp='xinput set-prop "ETPS/2 Elantech Touchpad"'

# These values are extracted from Xorg.0.log.
# It seems there is no other way to read them.
# https://wiki.archlinux.org/index.php/Touchpad_Synaptics
xrange=3260
yrange=1793

# Setting clickpad button regions.
# This touchpad has only one button under the entire touch surface.
# This command configures the clicking area such as:
#
# |0                                  (x range) 3260|
# |0%                40%       60%              100%|
# |-------------------+---------+-------------------|1470 (y position)
# |                   |         |                   |
# | Left              | Middle  |             Right |
#  '-----------------------------------------------' 1793 (y range)
#
# right button (left right top bottom) left button (left right top bottom)
xsp "Synaptics Soft Button Areas" \
	$(( xrange * 60 / 100 )) 0 1470 0 \
	$(( xrange * 40 / 100 )) $(( xrange * 60 / 100 )) 1470 0

# Right top tap
# Right bottom tap
# Left top tap
# Left bottom tap
# 1-finger tap: left click
# 2-finger tap: right click
# 3-finger tap: middle click
xsp "Synaptics Tap Action" 0 3 0 0 1 3 2
# left, right, top, bottom.
#xsp "Synaptics Edges" 130 3130 96 1697
xsp "Synaptics Edges" 1 $(( xrange * 60 / 100 )) 1 1470

# 1-finger click: left click
# 2-finger click: right click
# 3-finger click: middle click
# However, does not seem to actually work.
xsp "Synaptics Click Action" 1 3 2

# Vertical and horizontal scrolling.
xsp "Synaptics Two-Finger Scrolling" 1 1
xsp "Synaptics Circular Scrolling" 0
xsp "Synaptics Edge Scrolling" 0 0 0

# Natural scrolling, like Mac OS X, reverse of classical scrolling.
#xsp "Synaptics Scrolling Distance" 74 74
xsp "Synaptics Scrolling Distance" -74 -74

# I wish I could find good palm detection settings.
xsp "Synaptics Palm Detection" 0

# This is already the defaut.
xsp "Synaptics Locked Drags" 0

# This is already the defaut.
# AKA TapAndDragGesture.
xsp "Synaptics Gestures" 1

# min, max, accel, <deprecated>
#xsp "Synaptics Move Speed" 1.00 1.75 0.053763 0
xsp "Synaptics Move Speed" 1.0 1.50 0.05 0

#!/bin/sh

# See also: man synaptics

# (II) config/udev: Adding input device AlpsPS/2 ALPS DualPoint TouchPad (/dev/input/event7)
# (**) AlpsPS/2 ALPS DualPoint TouchPad: Applying InputClass "evdev touchpad catchall"
# (**) AlpsPS/2 ALPS DualPoint TouchPad: Applying InputClass "libinput touchpad catchall"
# (**) AlpsPS/2 ALPS DualPoint TouchPad: Applying InputClass "touchpad catchall"
# (**) AlpsPS/2 ALPS DualPoint TouchPad: Applying InputClass "Default clickpad buttons"
# (II) LoadModule: "synaptics"
# (II) Loading /usr/lib/xorg/modules/input/synaptics_drv.so
# (II) Module synaptics: vendor="X.Org Foundation"
# 	compiled for 1.19.3, module version = 1.9.0
# 	Module class: X.Org XInput Driver
# 	ABI class: X.Org XInput driver, version 24.1
# (II) Using input driver 'synaptics' for 'AlpsPS/2 ALPS DualPoint TouchPad'
# (**) AlpsPS/2 ALPS DualPoint TouchPad: always reports core events
# (**) Option "Device" "/dev/input/event7"
# (--) synaptics: AlpsPS/2 ALPS DualPoint TouchPad: x-axis range 0 - 2432 (res 34)
# (--) synaptics: AlpsPS/2 ALPS DualPoint TouchPad: y-axis range 0 - 1280 (res 34)
# (--) synaptics: AlpsPS/2 ALPS DualPoint TouchPad: pressure range 0 - 127
# (II) synaptics: AlpsPS/2 ALPS DualPoint TouchPad: device does not report finger width.
# (--) synaptics: AlpsPS/2 ALPS DualPoint TouchPad: buttons: left right middle double triple
# (--) synaptics: AlpsPS/2 ALPS DualPoint TouchPad: Vendor 0x2 Product 0x8
# (--) synaptics: AlpsPS/2 ALPS DualPoint TouchPad: invalid finger width range.  defaulting to 0 - 15
# (--) synaptics: AlpsPS/2 ALPS DualPoint TouchPad: touchpad found
# (**) AlpsPS/2 ALPS DualPoint TouchPad: always reports core events
# (**) Option "config_info" "udev:/sys/devices/platform/i8042/serio1/input/input6/event7"
# (II) XINPUT: Adding extended input device "AlpsPS/2 ALPS DualPoint TouchPad" (type: TOUCHPAD, id 14)
# (**) synaptics: AlpsPS/2 ALPS DualPoint TouchPad: (accel) MinSpeed is now constant deceleration 2.5
# (**) synaptics: AlpsPS/2 ALPS DualPoint TouchPad: (accel) MaxSpeed is now 1.75
# (**) synaptics: AlpsPS/2 ALPS DualPoint TouchPad: (accel) AccelFactor is now 0.073
# (**) AlpsPS/2 ALPS DualPoint TouchPad: (accel) keeping acceleration scheme 1
# (**) AlpsPS/2 ALPS DualPoint TouchPad: (accel) acceleration profile 1
# (**) AlpsPS/2 ALPS DualPoint TouchPad: (accel) acceleration factor: 2.000
# (**) AlpsPS/2 ALPS DualPoint TouchPad: (accel) acceleration threshold: 4
# (--) synaptics: AlpsPS/2 ALPS DualPoint TouchPad: touchpad found
# (II) config/udev: Adding input device AlpsPS/2 ALPS DualPoint TouchPad (/dev/input/mouse1)
# (**) AlpsPS/2 ALPS DualPoint TouchPad: Ignoring device from InputClass "touchpad ignore duplicates"
# (II) config/udev: Adding input device AlpsPS/2 ALPS DualPoint Stick (/dev/input/event6)
# (**) AlpsPS/2 ALPS DualPoint Stick: Applying InputClass "evdev pointer catchall"
# (**) AlpsPS/2 ALPS DualPoint Stick: Applying InputClass "trackpoint catchall"
# (**) AlpsPS/2 ALPS DualPoint Stick: Applying InputClass "libinput pointer catchall"
# (II) Using input driver 'libinput' for 'AlpsPS/2 ALPS DualPoint Stick'
# (**) AlpsPS/2 ALPS DualPoint Stick: always reports core events
# (**) Option "Device" "/dev/input/event6"
# (**) Option "_source" "server/udev"
# (II) input device 'AlpsPS/2 ALPS DualPoint Stick', /dev/input/event6 is tagged by udev as: Mouse Pointingstick
# (II) input device 'AlpsPS/2 ALPS DualPoint Stick', /dev/input/event6 is a pointer caps
# (**) Option "config_info" "udev:/sys/devices/platform/i8042/serio1/input/input8/event6"
# (II) XINPUT: Adding extended input device "AlpsPS/2 ALPS DualPoint Stick" (type: MOUSE, id 15)
# (**) Option "AccelerationScheme" "none"
# (**) AlpsPS/2 ALPS DualPoint Stick: (accel) selected scheme none/0
# (**) AlpsPS/2 ALPS DualPoint Stick: (accel) acceleration factor: 2.000
# (**) AlpsPS/2 ALPS DualPoint Stick: (accel) acceleration threshold: 4
# (II) input device 'AlpsPS/2 ALPS DualPoint Stick', /dev/input/event6 is tagged by udev as: Mouse Pointingstick
# (II) input device 'AlpsPS/2 ALPS DualPoint Stick', /dev/input/event6 is a pointer caps
# (II) config/udev: Adding input device AlpsPS/2 ALPS DualPoint Stick (/dev/input/mouse0)


xsp() {
	#xinput set-prop 'AlpsPS/2 ALPS DualPoint TouchPad' "$@"
	xinput set-prop 'AlpsPS/2 ALPS GlidePoint' "$@"
}

# These values are extracted from Xorg.0.log.
# It seems there is no other way to read them.
# https://wiki.archlinux.org/index.php/Touchpad_Synaptics
xrange=2432
yrange=1280

# Right top tap
# Right bottom tap
# Left top tap
# Left bottom tap
# 1-finger tap: left click
# 2-finger tap: right click
# 3-finger tap: middle click
xsp "Synaptics Tap Action" 0 0 0 0 1 3 2
# left, right, top, bottom.
#xsp "Synaptics Edges" 130 3130 96 1697
xsp "Synaptics Edges" 1 $(( xrange -1 )) 1 $(( yrange -1 ))

# Vertical and horizontal scrolling.
xsp "Synaptics Two-Finger Scrolling" 1 1
xsp "Synaptics Circular Scrolling" 0
xsp "Synaptics Edge Scrolling" 0 0 0

# Natural scrolling, like Mac OS X, reverse of classical scrolling.
#xsp "Synaptics Scrolling Distance" 54 54
xsp "Synaptics Scrolling Distance" -54 -54

# I wish I could find good palm detection settings.
xsp "Synaptics Palm Detection" 0

# This is already the defaut.
xsp "Synaptics Locked Drags" 0

# This is already the defaut.
# AKA TapAndDragGesture.
xsp "Synaptics Gestures" 1

# min, max, accel, <deprecated>
#xsp "Synaptics Move Speed" 1.00 1.75 0.053763 0
#xsp "Synaptics Move Speed" 1.0 1.50 0.05 0
xsp "Synaptics Move Speed" 1.0 1.0 0.0 0

# http://xorg.freedesktop.org/wiki/Development/Documentation/PointerAcceleration/#accelerationprofileinteger
xsp 'Device Accel Profile' -1
xsp 'Device Accel Constant Deceleration' 1.5
#xsp 'Device Accel Adaptive Deceleration' 1.000000
#xsp 'Device Accel Velocity Scaling' 12.500000


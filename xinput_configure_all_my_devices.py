#!/usr/bin/env python3
#
# Confused? Don't worry.
#
# This script is split into three main parts:
#
#  * Common predefined actions
#      -> These are either xinput or setxkbmap commands for specific settings.
#
#  * Rules
#      -> These map each device name with a list of actions.
#
#  * Main code
#      -> No need to modify any of the main code.
#
# Before each part, there is a line full of '#' characters,
# making it easy to jump between each part.
#
# There is no external configuration file, this script is the configuration.
# Adapt it to your needs, and have fun!


import argparse
import os
import re
import shlex
import subprocess
from collections import defaultdict, namedtuple


######################################################################
# Common actions that may be reused for multiple devices.
#
# Need help? Try these:
# * xinput --help
# * man xinput
# * man -a libinput
# * man 4 libinput
# * man synaptics
# * man xkeyboard-config
# * /var/log/Xorg.0.log
# * https://wiki.archlinux.org/index.php/Touchpad_Synaptics
# * https://wiki.archlinux.org/index.php/Mouse_acceleration#Disabling_mouse_acceleration
# * http://xorg.freedesktop.org/wiki/Development/Documentation/PointerAcceleration/#accelerationprofileinteger

FLAT_ACCEL_PROFILE = [
    ['set-prop', 'libinput Accel Profile Enabled', 0, 1],
]
MIDDLE_CLICK_EMULATION = [
    ['set-prop', 'libinput Middle Emulation Enabled', 1],
]
NATURAL_SCROLLING = [
    ['set-prop', 'libinput Natural Scrolling Enabled', 1],

    #    _______
    #   /  | |  \   Scroll:
    #  | 1 |2| 3 |    4
    #  |   |_|   |  6<@>7
    #  |         |    5
    # []9 Forward|
    #  |         |
    # []8 Back   |
    #  |         |
    #   \_______/

    # Inverting horizontal scroll buttons: 6 and 7
    # But this has no effect in Chrome. :(
    # https://gitlab.freedesktop.org/libinput/libinput/issues/195
    # https://crbug.com/913403
    # ['set-button-map', 1, 2, 3, 4, 5, 7, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],

    # Side buttons are now middle-click (8,9 = 2)
    # ['set-button-map', 1, 2, 3, 4, 5, 6, 7, 2, 2],

    # Side buttons are now horizontal scroll (8,9 = 6,7)
    # ['set-button-map', 1, 2, 3, 4, 5, 6, 7, 6, 7],
]

TOUCHPAD_TAP_TO_CLICK = [
    ['set-prop', 'libinput Tapping Enabled', 1],
]

TOUCHPAD_COMMON_SETTINGS = [
    # Vertical and horizontal scrolling.
    ['set-prop', 'Synaptics Two-Finger Scrolling', 1, 1],
    ['set-prop', 'Synaptics Circular Scrolling', 0],
    ['set-prop', 'Synaptics Edge Scrolling', 0, 0, 0],

    # I wish I could find good palm detection settings.
    ['set-prop', 'Synaptics Palm Detection', 0],

    # This is already the defaut.
    ['set-prop', 'Synaptics Locked Drags', 0],

    # This is already the defaut. AKA TapAndDragGesture.
    ['set-prop', 'Synaptics Gestures', 1],

    # min, max, accel, <deprecated>
    # ['set-prop', 'Synaptics Move Speed', 1.00, 1.75, 0.053763, 0],
    # ['set-prop', 'Synaptics Move Speed', 1.00, 1.50, 0.05, 0],
    ['set-prop', 'Synaptics Move Speed', 1.0, 1.0, 0.0, 0],

    # http://xorg.freedesktop.org/wiki/Development/Documentation/PointerAcceleration/#accelerationprofileinteger
    # Defaults:
    # ['set-prop', 'Device Accel Profile', 1],
    # ['set-prop', 'Device Accel Constant Deceleration', 2.5],
    # ['set-prop', 'Device Accel Adaptive Deceleration', 1.000000],
    # ['set-prop', 'Device Accel Velocity Scaling', 12.500000],

    # Profiles:
    # -1. none
    # 1. device-dependent
    # 2. polynomial
    # 3. smooth linear
    # 4. simple
    # 5. power
    # 6. linear
    # 7. limited
    ['set-prop', 'Device Accel Profile', -1],

    # Tweaking the touchpad cursor speed.
    ['set-prop', 'Device Accel Constant Deceleration', 1.25],
]


# x_range/y_range values are extracted from Xorg.0.log.
# It seems there is no other way to read them.
# https://wiki.archlinux.org/index.php/Touchpad_Synaptics
def TOUCHPAD_MINIMUM_EDGES(x_range, y_range):
    return [
        # left, right, top, bottom.
        # ['set-prop', 'Synaptics Edges', 130, 3130, 96, 1697],
        ['set-prop', 'Synaptics Edges', 1, x_range - 1, 1, y_range - 1],
    ]


def TOUCHPAD_EDGES_AND_SOFT_BUTTONS(x_range, y_range, x_perc1=40, x_perc2=60, y_perc=80):
    x_pos1 = round(x_range * x_perc1 / 100)
    x_pos2 = round(x_range * x_perc2 / 100)
    y_pos = round(y_range * y_perc / 100)
    return [
        # left, right, top, bottom.
        ['set-prop', 'Synaptics Edges', 1, x_pos2, 1, y_pos],

        # Setting clickpad button regions.
        # This touchpad has only one button under the entire touch surface.
        # This command configures the clicking area such as:
        #
        # |0                 pos1      pos2   (x_range) 3260|
        # |0%                40%       60%              100%|
        # |-------------------+---------+-------------------|1470 (y_pos)
        # |                   |         |                   |
        # | Left              | Middle  |             Right |
        #  '-----------------------------------------------' 1793 (y_range)
        #
        # right button (left right top bottom) left button (left right top bottom)
        [
            'set-prop', 'Synaptics Soft Button Areas',
            x_pos2, 0, y_pos, 0,
            x_pos1, x_pos2, y_pos, 0
        ],
    ]


######################################################################
# Rules, mapping device names to actions.

RULES_LIST = [
    # Format:
    #   3-item tuple:
    #     * 'keyboard' or 'pointer' as string.
    #     * list of device names (each as a string)
    #     * list of actions (each as a list of strings or numbers)
    #
    # Example:
    # (
    #     'keyboard or pointer',         # Device type as string
    #     [                              # List of device names
    #         'Device foo',
    #         'Device bar',
    #     ],
    #     [                              # List of actions (for either xinput or setxkbmap)
    #         ['set-prop', 'foo', 1, 2, 3],
    #         ['setxkbmap', 'foo', 'bar'],
    #     ],
    # )
    #
    # For convenience, you can use list expansion to reuse the same predefined
    # actions across multiple devices.

    # Mouse devices.
    (
        'pointer',
        [
            'Microsoft  Microsoft Basic Optical Mouse v2.0',
            'Corsair Gaming HARPOON RGB Mouse',
            'Logitech USB Laser Mouse',
            'Logitech M705',
            'Logitech MX Master 2S',
            'MX Master 2S',
            'MX Master 2S Mouse',
            'PixArt Dell MS116 USB Optical Mouse',
            'YICHIP Wireless Device Mouse',
        ],
        [
            *FLAT_ACCEL_PROFILE,
            # *NATURAL_SCROLLING,
        ]
    ),
    (
        'pointer',
        [
            # This is actually a touchpad, but behaves like a mouse.
            # The touchpad is not configurable without the proprietary Logitech tool.
            # Pinching gestures generate Ctrl+mouse-scroll input.
            'Logitech K400 Plus',
        ],
        [
            *FLAT_ACCEL_PROFILE,
            *NATURAL_SCROLLING,
            *MIDDLE_CLICK_EMULATION,
        ]
    ),

    # Keyboard devices.
    (
        'keyboard',
        [
            # Asus X450C laptop
            # Dell Latitude 7300 laptop
            'AT Translated Set 2 keyboard',
        ],
        [
            # First to clear the previously set options
            ['setxkbmap', '-option'],
            [
                'setxkbmap', 'us', 'altgr-intl',

                # Position of Compose key
                #'compose:menu',
                'compose:caps',

                # Caps Lock behavior
                #'caps:backspace',
                #'caps:none',

                # Num Lock on: digits; Shift for arrows. Num Lock off: arrows (as in Windows)
                #'numpad:microsoft',

                # Numeric keypad always enters digits (as in macOS)
                'numpad:mac',
            ],
        ]
    ),
    (
        'keyboard',
        [
            'Logitech K400 Plus',

            'Logitech MX Keys',
        ],
        [
            # First to clear the previously set options
            ['setxkbmap', '-option'],
            [
                'setxkbmap', 'us', 'altgr-intl',
                'compose:caps',
            ],
        ]
    ),
    (
        'keyboard',
        [
            # idVendor=05ac, idProduct=026c
            'Apple Inc. Magic Keyboard with Numeric Keypad',
        ],
        [
            # https://unix.stackexchange.com/q/86933
            # First to clear the previously set options
            ['setxkbmap', '-option'],
            # Then to set the options. (man xkeyboard-config)
            # * Capslock is another backspace.
            # * Bottom-left modifiers are: Ctrl, Super, Alt
            # * Bottom-right modifiers are: AltGr, Compose, Ctrl
            # * F13, F14, F15 are PrtScn/SysRq, Scroll Lock, Pause/Break
            [
                'setxkbmap', 'us', 'altgr-intl',
                #'caps:backspace',
                'numpad:microsoft',
                'compose:rwin',
                'compose:caps',
                #'altwin:swap_alt_win',
                'apple:alupckeys',  # Emulate PC keys
                'lv3:ralt_switch',  # Third level, useful for deadkeys.
            ],

            # fn is in place of the usual Insert key.
            # Thus, remapping Eject to Insert
            # xmodmap -e 'keysym XF86Eject = Insert NoSymbol Insert'
        ]
    ),

    # Touchpad devices.
    (
        'pointer',
        [
            # Asus X450C laptop.
            'ETPS/2 Elantech Touchpad',

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
        ],
        [
            *TOUCHPAD_COMMON_SETTINGS,
            *TOUCHPAD_EDGES_AND_SOFT_BUTTONS(3260, 1793, 40, 60, 82),

            # Natural scrolling, like Mac OS X, reverse of classical scrolling.
            ['set-prop', 'Synaptics Scrolling Distance', -74, -74],

            # Tapping settings:
            # Right top tap
            # Right bottom tap
            # Left top tap
            # Left bottom tap
            # 1-finger tap: left click
            # 2-finger tap: right click
            # 3-finger tap: middle click
            ['set-prop', 'Synaptics Tap Action', 0, 3, 0, 0, 1, 3, 2],

            # Clicking settings (for a clickable touchpad, without dedicated buttons):
            # 1-finger click: left click
            # 2-finger click: right click
            # 3-finger click: middle click
            ['set-prop', 'Synaptics Click Action', 1, 3, 2],

        ]
    ),
    (
        'pointer',
        [
            # Dell E7270 laptop.
            'AlpsPS/2 ALPS DualPoint TouchPad',
            'AlpsPS/2 ALPS GlidePoint',

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
        ],
        [
            *TOUCHPAD_COMMON_SETTINGS,
            *TOUCHPAD_MINIMUM_EDGES(2432, 1280),

            # Natural scrolling, like Mac OS X, reverse of classical scrolling.
            ['set-prop',  'Synaptics Scrolling Distance', -54, -54],

            # Tapping settings:
            # Right top tap
            # Right bottom tap
            # Left top tap
            # Left bottom tap
            # 1-finger tap: left click
            # 2-finger tap: right click
            # 3-finger tap: middle click
            ['set-prop', 'Synaptics Tap Action', 0, 0, 0, 0, 1, 3, 2],
        ]
    ),

    (
        'pointer',
        [
            # Dell Latitude 7300 laptop
            'DELL08E0:00 06CB:CD97 Touchpad',
        ],
        [
            *TOUCHPAD_TAP_TO_CLICK,
            *NATURAL_SCROLLING,
            #*FLAT_ACCEL_PROFILE,
        ]
    ),

    # Do-nothing rules.
    # They exist just to avoid reporting these devices as unrecognized.
    (
        'pointer',
        [
            'Virtual core XTEST pointer',

            # This is a keyboard, not a mouse.
            'Logitech MX Keys',

            # Cheap wireless mouse.
            'YICHIP Wireless Device Consumer Control',

            # Dell Latitude 7300 laptop, fake mouse devices that are not used.
            'DELL08E0:00 06CB:CD97 Mouse',
            'PS/2 Generic Mouse',

            # Dell dock connected to USB-C.
            # Or possibly any external display. I don't know.
            'DP-1',
            'DP-2',
        ],
        []
    ),
    (
        'keyboard',
        [
            'Aeropex by AfterShokz (AVRCP)',
            'Asus WMI hotkeys',
            'Asus Wireless Radio Control',
            'DELL Wireless hotkeys',
            'Dell WMI hotkeys',
            'HP WMI hotkeys',
            'Integrated_Webcam_HD: Integrate',
            'Intel HID 5 button array',
            'Intel HID events',
            'Logitech MX Master 2S',
            'MX Master 2S Keyboard',
            'MX Master 2S',
            'Power Button',
            'Sleep Button',
            'USB Camera: USB Camera',
            'Vaydeer Vaydeer Multimedia Console Keyboard',
            'Video Bus',
            'Virtual core XTEST keyboard',
            'Yubico Yubikey 4 OTP+U2F',

            # Cheap wireless mouse.
            'YICHIP Wireless Device',
            'YICHIP Wireless Device System Control',
            'YICHIP Wireless Device Consumer Control',

            # Dell dock connected to USB-C.
            # Or possibly any external display. I don't know.
            'DP-1',
            'DP-2',
        ],
        []
    ),
]


######################################################################
# No need to modify anything below this line.

# Custom lightweight object type.
XInputDevice = namedtuple('XInputDevice', 'type id name')
# Compiling the regex during the module load.
xinput_regex = re.compile(r'^.   ↳ (.*[^ ]) *\tid=([0-9]+)\t\[slave +(pointer|keyboard) +\([0-9]+\)\]')
xinput_ignored_regex = re.compile(r'^. Virtual core (pointer|keyboard) +\tid=([0-9]+)\t\[master +(pointer|keyboard) +\([0-9]+\)\]')


def rules_as_dict(rules_list):
    '''Converts rules_list into a dictionary for fast access.

    It will also convert any non-string parameter into a string.

    The result of this function can be used as this:
        d = rules_as_dict()
        action_list = d['pointer', 'Mouse ABCXYZ']  # Can cause KeyError exception!
        action_list = d.get(('pointer', 'Mouse ABCXYZ'), [])  # Much better!
    Where action_list will be a list of xinput commands.
    '''
    d = defaultdict(list)
    for rule in rules_list:
        (dev_type, dev_names, actions) = rule
        actions_as_str = [
            [str(x) for x in action] for action in actions
        ]
        for name in dev_names:
            d[dev_type, name].extend(actions_as_str)
    # Disabling the defaultdict behavior, making it behave just like a normal dict.
    d.default_factory = None
    return d


def xinput_list():
    '''Generator that returns XInputDevice objects based on `xinput list` output.

    Note that `xinput list --name-only` is trivial to parse, but it omits the
    device type (pointer or keyboard). Thus, this function parses the default
    output format (which is the same as `--short`).
    '''
    p = subprocess.run(
        ['xinput', 'list'],
        check=True,
        # capture_output=True,  # added in Python 3.7
        stdout=subprocess.PIPE, stderr=subprocess.PIPE  # equivalent to capture_output=True
    )
    text = p.stdout.decode('utf8', 'replace')
    for line in text.splitlines():
        match = xinput_regex.match(line)
        if match:
            yield XInputDevice(name=match.group(1), id=match.group(2), type=match.group(3))
        else:
            match = xinput_ignored_regex.match(line)
            if not match:
                print('Warning! Unrecognized line from `xinput list` output: {0!r}'.format(line))


def build_cmdline_args(device, action):
    '''Builds the command-line to be executed.

    Has extra logic to inject the device id, and to select either xinput or
    setxkbmap.
    '''
    (head, *tail) = action
    id = str(device.id)
    if head == 'setxkbmap':
        return ['setxkbmap', '-device', id, *tail]
    else:
        return ['xinput', head, id, *tail]


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Uses xinput to configure available devices to my preferences'
    )
    parser.add_argument(
        '-n', '-d', '--dry-run', '--dryrun',
        action='store_true',
        dest='dryrun',
        help='Don\'t run any actions for the detected devices. Useful while testing this script, goes well with --verbose.',
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='verbose',
        help='Print each executed command for each device.',
    )
    options = parser.parse_args()
    return options


def main():
    options = parse_arguments()
    rules = rules_as_dict(RULES_LIST)

    # Setting up the 'C' locale to prevent any issue related to localization or translation.
    os.environ['LC_ALL'] = 'C'

    # For each detected device...
    for device in xinput_list():
        actions = rules.get((device.type, device.name), None)
        if actions is None:
            print('Ignoring {0.type} device {0.id} ({0.name}), because there are no rules matching this device'.format(device))
        else:
            if options.verbose:
                if len(actions) == 0:
                    print('There are no actions for {0.type} device {0.id} ({0.name})'.format(device))
                else:
                    print('Setting up {0.type} device {0.id} ({0.name})'.format(device))
            for action in actions:
                # Preparing the command-line.
                args = build_cmdline_args(device=device, action=action)

                # The shell-friendly string version of the command-line.
                # Only used for debugging purposes.
                cmdline = ' '.join(shlex.quote(arg) for arg in args)
                if options.verbose:
                    print('{1}Running: {0}'.format(cmdline, '(dry-run) ' if options.dryrun else ''))

                # Running! This is the main purpose of this whole script! :)
                if options.dryrun:
                    pass
                else:
                    p = subprocess.run(args)
                    if p.returncode != 0:
                        print('Warning! Command returned {0}: {1}'.format(p.returncode, cmdline))


if __name__ == '__main__':
    main()

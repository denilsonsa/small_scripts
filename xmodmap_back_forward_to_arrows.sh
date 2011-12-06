#!/bin/sh

# The problem:
# Some keyboards (like those from Lenovo Thinkpad) have "Back" and "Forward"
# buttons placed together with the arrow keys, like this:
# +--------------------+
# | Shift              |
# +------+------+------+
# | Back |  Up  | Frwd |
# +------+------+------+
# | Left | Down | Right|
# +------+------+------+
# http://www.thinkpads.com/2009/08/31/finally-photos-of-new-thinkpad-usb-trackpoint-keyboard/
#
# So, whenever I try to use the arrow keys, I end up pressing Back/Forward
# buttons instead, which usually makes the browser go back/forward into the
# history, and I lose what I typed and I get mad.
#
# The solution:
# Remapping those keys to Left/Right arrows


# Default:
# keycode 166 = XF86Back NoSymbol XF86Back
# keycode 167 = XF86Forward NoSymbol XF86Forward

# Remapping to arrow keys:
#xmodmap -e 'keycode 166 = Left NoSymbol Left'
#xmodmap -e 'keycode 167 = Right NoSymbol Right'

xmodmap -e 'keysym XF86Back = Left NoSymbol Left'
xmodmap -e 'keysym XF86Forward = Right NoSymbol Right'

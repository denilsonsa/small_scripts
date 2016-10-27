#!/bin/sh
# META:ICON = "video-asusM51Sn-at-right.png"

# http://blog.siddv.net/2014/09/turning-laptop-screen-into-external.html
# I have turned my old Asus M51Sn notebook display into an external monitor.
# I'm using it in the portrait orientation.
# The controller board I bought does not have built-in support for the native
# resolution (for some reason). That's why I need to add the resolution manually.

# See also: create-virtual-modelines.sh
# And also: gtf 1280 800 60
# And also: cvt 1280 800 60
set -x
xrandr --delmode HDMI-1 1280x800_60
xrandr --rmmode 1280x800_60
xrandr --newmode 1280x800_60 83.46  1280 1344 1480 1680  800 801 804 828  -HSync +Vsync
xrandr --addmode HDMI-1 1280x800_60
xrandr --dpi 96x96 --output HDMI-1 --mode 1280x800_60 --pos 1366x0 --rotate left --output LVDS-1 --primary --mode 1366x768 --pos 0x512 --rotate normal --output VIRTUAL-1 --off --output DP-1 --off --output VGA-1 --off
~/myrepos/small_scripts/wallpaper_restore.sh
~/.screenlayout/wacom-desktop.sh
~/myrepos/small_scripts/skippy-xd-restart.sh

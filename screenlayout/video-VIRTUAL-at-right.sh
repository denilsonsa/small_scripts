#!/bin/sh
# META:ICON = "video-VIRTUAL-at-right.png"
xrandr --output VIRTUAL2 --off --output VIRTUAL1 --mode 1920x1000_60.00 --pos 1366x0 --rotate normal --output DP1 --off --output HDMI1 --off --output LVDS1 --mode 1366x768 --pos 0x232 --rotate normal --output VGA1 --off
~/myrepos/small_scripts/wallpaper_restore.sh

#!/bin/sh
# META:ICON = "video-mirrored.png"
xrandr --output HDMI1 --mode 1360x768 --pos 0x0 --rotate normal --output LVDS1 --mode 1366x768 --pos 0x0 --rotate normal --primary --output VIRTUAL1 --off --output DP1 --off --output VGA1 --off
~/myrepos/small_scripts/wallpaper_restore.sh
~/.screenlayout/audio-to-HDMI.sh
~/.screenlayout/wacom-desktop.sh

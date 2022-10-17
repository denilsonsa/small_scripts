#!/bin/sh
# META:ICON = "video-1080p-vertical-at-right.png"
xrandr --dpi 96x96 --output LVDS-1 --primary --mode 1366x768 --pos 0x1152 --rotate normal --output DP-1 --off --output HDMI-1 --mode 1920x1080 --pos 1366x0 --rotate left --output VGA-1 --off
~/myrepos/small_scripts/wallpaper_restore.sh
~/.screenlayout/audio-to-HDMI.sh
~/.screenlayout/wacom-desktop.sh
~/myrepos/small_scripts/skippy-xd-restart.sh

# --dpi 96x96 because: https://www.reddit.com/r/chrome/comments/36u42i/psa_set_dpi_to_96x96_to_fix_several_chrome_43/

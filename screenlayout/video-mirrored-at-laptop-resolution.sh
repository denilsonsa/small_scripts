#!/bin/sh
# META:ICON = "video-mirrored.png"
xrandr --dpi 96x96 --output HDMI-1 --mode 1360x768 --pos 0x0 --rotate normal --output LVDS-1 --mode 1366x768 --pos 0x0 --rotate normal --primary --output VIRTUAL-1 --off --output DP-1 --off --output VGA-1 --off
~/myrepos/small_scripts/wallpaper_restore.sh
~/.screenlayout/audio-to-HDMI.sh
~/.screenlayout/wacom-desktop.sh
~/myrepos/small_scripts/skippy-xd-restart.sh
~/myrepos/small_scripts/skippy-xd-restart.sh

# --dpi 96x96 because: https://www.reddit.com/r/chrome/comments/36u42i/psa_set_dpi_to_96x96_to_fix_several_chrome_43/

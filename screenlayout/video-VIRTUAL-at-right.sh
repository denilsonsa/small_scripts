#!/bin/sh
# META:ICON = "video-VIRTUAL-at-right.png"
xrandr --dpi 96x96 --output VIRTUAL2 --off --output VIRTUAL1 --mode 1920x1000_60.00 --pos 1366x0 --rotate normal --output DP1 --off --output HDMI1 --off --output LVDS1 --mode 1366x768 --pos 0x232 --rotate normal --output VGA1 --off
~/myrepos/small_scripts/wallpaper_restore.sh

# --dpi 96x96 because: https://www.reddit.com/r/chrome/comments/36u42i/psa_set_dpi_to_96x96_to_fix_several_chrome_43/

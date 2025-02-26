#!/bin/sh
xrandr --dpi 96x96 \
	--output DP-1 --mode 2560x1440 --pos    0x0 --rotate left --primary \
	--output DP-2 --mode 2560x1440 --pos 1440x0 --rotate left \
	--output DP-3 --off \
	--output HDMI-1 --off \
	--output HDMI-2 --off

# --dpi 96x96 because: https://www.reddit.com/r/chrome/comments/36u42i/psa_set_dpi_to_96x96_to_fix_several_chrome_43/

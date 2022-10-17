#!/bin/sh
# META:ICON = "video-only-laptop.png"
xrandr --dpi 96x96 \
    --output eDP-1 --primary --mode 1920x1080 --pos 0x0 --rotate normal \
    --output DP-1   --off \
    --output DP-2   --off \
    --output HDMI-1 --off \
    --output HDMI-2 --off

# On KDE Plasma, I think I don't need to manually restore the wallpapers.
# Still, in case I need, I can call a script like this:
# ~/stuff/wallpaper_restore.sh

# --dpi 96x96 because: https://www.reddit.com/r/chrome/comments/36u42i/psa_set_dpi_to_96x96_to_fix_several_chrome_43/

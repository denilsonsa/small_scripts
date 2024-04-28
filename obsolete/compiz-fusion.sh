#!/bin/sh

# I could have used /usr/bin/compiz-manager instead of this script.

# This might be useful (not sure what it does): --ignore-desktop-hints
# This might improve performance on nvidia: --loose-binding
# See (INSERT compiz-fusion wiki URL here)
compiz --loose-binding --replace ccp &
#compiz --replace ccp &
COMPIZ_PID=$!

# compiz --ignore-desktop-hints --replace --loose-binding --replace core ccp &

#gtk-window-decorator &
emerald --replace &
DECORATOR_PID=$!

#numlock

fbpanel &

fbsetbg -l

sleep 10

glista &

# From gnome-bluetooth
bluetooth-applet &

#( cd /tmp/software/batterymon-svn/ && ./batterymon.py -t denilsonsa & )
#{ cd /tmp/software/batterymon-local-hg/ && ./batterymon.py -t 16x16 ; } &
{ cd /tmp/software/batterymon-clone/ && ./batterymon -t 16x16 ; } &

#fbsetbg -l
#fbsetroot -solid '#446699'

wait $COMPIZ_PID $DECORATOR_PID

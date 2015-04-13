#!/bin/sh

# Runs x11vnc on a virtual screen, as described in:
# https://bbs.archlinux.org/viewtopic.php?id=191555

# -clip           Accepts either a geometry (WxH+X+Y) or the name of a xinerama screen.
# -forever        Is the opposite of -once, and will keep x11vnc running even after the client disconnects.
# -tightfilexfer  Enables TightVNC file transfer extension.
# -nolookup       Do not try DNS lookups.
# -nowireframe    Upon window moving, do not display just the wireframe.

# Zenity, for some weird reason, prints the column twice, separated by separator.
screen="$(zenity --list --hide-header --title='x11vnc pre-setup' \
	--text='Restrict to a single screen?' \
	--column='Label' --column='value' --hide-column=2 --print-column=2 --separator='WTF' \
	'Entire desktop' 'x' \
	'Xinerama 0' 'xinerama0' \
	'Xinerama 1' 'xinerama1' | sed 's/WTF.*//')" || exit

if [ -n "${screen}" ]; then
	clip_options="-clip ${screen}"
fi

x11vnc ${clip_options} -passwdfile 'cmd:zenity --password --title x11vnc' -forever -tightfilexfer -nolookup -nowireframe -allow 192.168.0.100

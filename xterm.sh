#!/bin/bash
#
# Written by Denilson Figueiredo de Sa <denilsonsa@gmail.com>
# 2008-01-16 - Added this changelog. :)
# 2005-??-?? - First version written.

# Yeah, this script requires bash. It won't work on dash because this script
# uses [[ and pattern-matching. Rewriting this script to remove these bash-isms
# does not make much sense, because the script will be a lot uglier, and
# because the purpose of this script is to open an X terminal which will (most
# of the time) run bash!

# HOWTO INSTALL instructions:
# - Rename this script to xterm.sh
# - Put this script in a directory available at PATH (maybe ~/bin/)
# - At the same directory, create some symbolic links, using these commands:
#   ln -s xterm.sh bigxterm.sh
#   ln -s xterm.sh aterm.sh
#   ln -s aterm.sh bigaterm.sh


# -u8 is auto-detected if locale has UTF-8
COMMON="-rv -ls +sb -sl 1000 +sm"
NORMALSIZE="-font 6x13 -geometry 80x25"
#BIGSIZE="-font 10x20 -geometry 95x37+0+0"
BIGSIZE="-font 10x20 -geometry 95x37"

SCRIPTNAME=`basename "$0"`

if [[ "$SCRIPTNAME" == *big* ]]; then
	SIZE="$BIGSIZE"
else
	SIZE="$NORMALSIZE"
fi

if [[ "$SCRIPTNAME" == *aterm* ]]; then
	COLOR=$(echo | awk '{ srand(); printf "rgb:%02X/%02X/%02X", int(rand()*128+128), int(rand()*128+128), int(rand()*128+128) }')
	exec aterm $COMMON $SIZE -tr -tint "${COLOR}" -tinttype and -fade 60 -sh 40 -title "aterm - ${COLOR}" "$@"
elif [[ "$SCRIPTNAME" == *xterm* ]]; then
	exec xterm $COMMON $SIZE "$@"
else
	cat << EOF
Incorrect install of this script.

This script must be called using a filename with "xterm" or "aterm".
In addition, if there is "big" in name, the terminal will be run full-screen
(at least for my 1024x768 with a dockapps visible at right).

Example of a correct installation:
$  ls -o *term*
lrwxrwxrwx  1 denilson    8 Dec 19 11:59 aterm.sh -> xterm.sh
lrwxrwxrwx  1 denilson    8 Dec 19 11:59 bigaterm.sh -> aterm.sh
lrwxrwxrwx  1 denilson    8 Dec 19 11:59 bigxterm.sh -> xterm.sh
-rwxr-xr-x  1 denilson 1104 Dec 19 12:05 xterm.sh

Note that there are four ways of calling this script. Each one will run a
different terminal with a different size.
EOF
fi

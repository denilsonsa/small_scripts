#!/bin/bash
#
# This script is based on https://unix.stackexchange.com/a/593779
# Official documentation: https://docs.kde.org/stable5/en/konsole/konsole/command-line-options.html

SAVEFILE="${XDG_CONFIG_HOME:-$HOME/.config}/konsole/konsole_saved_tabs"

# There should be only one Konsole PID, but let's make it a loop anyway.
for KPID in `pgrep -u ${USER} --exact konsole` ; do
	for SES in `qdbus org.kde.konsole-${KPID} | grep /Sessions/` ; do
		SID="${SES#/Sessions/}"

		# I'm not saving the tab title format.
		# Also because I cannot compare if it was changed from the default.
		# FMT=`qdbus org.kde.konsole-${KPID} ${SES} tabTitleFormat 0`

		# PID of the shell running inside the terminal:
		PID=`qdbus org.kde.konsole-${KPID} ${SES} processId`
		DIR=`pwdx ${PID}`
		echo $KPID $SID $PID $FMT $DIR children: `pgrep --parent $PID`
	done
done

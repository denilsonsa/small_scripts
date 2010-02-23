#!/bin/bash

for VID in "$@" ; do
	LEN=`midentify "$VID" | sed -n 's/.*ID_LENGTH=\(.*\)/\1/p'`
	if which printf &> /dev/null ; then
		printf "%7s  %s\n" "$LEN" "$VID"
	else
		echo "$LEN  $VID"
	fi
done

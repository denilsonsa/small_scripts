#!/bin/bash

# fat2ext.sh - version 1.1 - 2003-11-16
# Created by Denilson F. de Sa
# 
# This thing fix the permissions after you copy anything
# from a FAT partition to a ext2/ext3 one.
# 
# This version is recursive and verbose. It changes all
# files to 644 and all directories to 755.
# 
# This script calls itself recursively to go deeper inside
# directory tree.
# 
# This script is very verbose, it tells you ALL changes that
# are made. Pipe it to a LOGFILE to see if everything is OK,
# or to /dev/null if you dare! :) I'm not responsible if
# anything goes wrong!


# TODO / WishList
# Create two more command-line options to ONLY change
# files/directories that have <supplied> permissions.


FILES=644
DIRS=755


print_help()
{
echo "fat2ext.sh - version 1.1 - 2003-11-16"
echo "Usage:" `basename $0` " <directory> [ file_permissions  dir_permissions ]"
echo "Default permissions are 644 for files and 755 for directories"
}


if [[ ($# != 3 && $# != 1) || "$1" == "-help" || "$1" == "--help" || "$1" == "-h" || "$1" == "-?" ]]; then
	print_help
else

	echo RUNNED AS "$*"

	if [ "$3" != "" ]; then
		FILES="$2"
		DIRS="$3"
	fi

	#Changing workind dir
	PODEIR=0
	cd "$1" && PODEIR=1

	#If changed, ok, go on!
	if [ $PODEIR == 1 ]; then
		pwd
		chmod -v $FILES *
		ls -1F --color=no | sed -n 's/\/$//p' | xargs -iAAA chmod -v $DIRS AAA
		ls -1F --color=no | sed -n 's/\/$//p' | xargs -iAAA "$0" AAA "$FILES" "$DIRS"
	fi

fi

#!/bin/bash

ABOUT='fat2ext.sh - version 1.2 - 2005-10-04
Created by Denilson F. de Sa'
# 
# This thing fix the permissions after you copy anything
# from a FAT partition to a ext2/ext3 one.
# 
# In fact, this script will change all directories permissions
# to 755 and all files to 644. Any previous special permissions
# are discarded.
#
# 755 and 644 are the default permissions. They can be changed
# using command-line parameters.


# TODO / WishList
# Create two more command-line options to ONLY change
# files/directories that have <supplied> permissions.


FILES=644
DIRS=755
VERBOSE=""
#VERBOSE="-v"


print_help()
{
echo "$ABOUT"
echo
echo "Usage:" `basename $0` " <directory> [ file_permissions  dir_permissions ]"
echo "Default permissions are 644 for files and 755 for directories"
}


if [[ ($# != 3 && $# != 1) || "$1" == "-help" || "$1" == "--help" || "$1" == "-h" || "$1" == "-?" ]]; then
	print_help
else

	if [ "$3" != "" ]; then
		FILES="$2"
		DIRS="$3"
	fi

	#This will give read permission to all files (and directories).
	#After this command, 'find' will be able to access the entire directory tree.
	chmod -R +rx "$1"

	find "$1" | ( while read line; do
		if [ -d "$line" ] ;	then
			chmod $VERBOSE "$DIRS" "$line"
		elif [ -f "$line" ] ; then
			chmod $VERBOSE "$FILES" "$line"
		else
			echo "Warning: '$line' is not a directory and is not a regular file."
		fi
	done )

fi

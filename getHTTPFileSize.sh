#!/bin/bash
# getHTTPFileSize.sh - version 1.0 - 2004-02-29
# Created by Denilson F. de Sa

# TODO
# - Add support to show HTTP and wget errors

print_help()
{
echo "getHTTPFileSize.sh - version 1.0 - 2004-02-29"
echo "Usage: " `basename $0` " '<address>'"
echo "Where <address> is the complete URL of the file."
echo ""
echo "This little script will retrieve headers from given URL and show the size of file, in bytes, kilobytes and megabytes (using division by 1024, and NOT 1000)."
}

print_wget_notfound()
{
	echo "ERROR: wget was not found."
	echo "This script uses wget, so you must have it somewhere in path."
}

print_sed_notfound()
{
	echo "ERROR: sed was not found."
	echo "This script uses sed, so you must have it somewhere in path."
}

if [[ $# != 1 ]]; then
	print_help
else
	if ! which "wget" &>/dev/null; then
		print_wget_notfound
	fi
	if ! which "sed" &>/dev/null; then
		print_sed_notfound
	fi

	LENGTH=`wget -S --spider "$1" 2>&1 | sed -n 's/^.*Content-Length: *\([0-9]\+\) *$/\1/p'`
	if [[ "$LENGTH" != "" ]]; then
		echo "File size is: $(($LENGTH)) bytes, $(($LENGTH/1024)) KB and $(($LENGTH/1048576)) MB."
	else
		echo "File size is unknown."
	fi
fi

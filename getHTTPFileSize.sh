#!/bin/sh
#
# Written by Denilson Figueiredo de Sa <denilsonsa@gmail.com>
# 2008-02-02 - Fixed this script to work even when the server redirects to
#              another URL. In this case, sometimes there are more than one
#              Content-Length line, which is now handled properly.
# 2008-01-20 - Removed bash dependency (now works also with dash).
#              First time this script was published on my site.
# 2004-02-29 - First version written.

# TODO
# - Add support to show HTTP and wget errors

MYNAME=`basename "$0"`

print_help()
{
	cat << EOF
Usage: $MYNAME <URL>

This script will use wget to get the HTTP headers from the server and then
parse these headers to print the file size (as reported by the server) in
human-readable values.

Only HTTP is supported.
EOF
}

if [ "$#" != "1" -o "$1" = "-h" -o "$1" = "--help" ]; then
	print_help
else
	LENGTH=`wget -S --spider "$1" 2>&1 | sed -n 's/^.*Content-Length: *\([0-9]\+\) *$/\1/p' | tail -n 1`
	if [ "$LENGTH" != "" ]; then
		echo "File size is: $(($LENGTH)) bytes, $(($LENGTH/1024)) KiB and $(($LENGTH/1024/1024)) MiB."
	else
		echo "File size is unknown."
	fi
fi

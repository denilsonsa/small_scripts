#!/bin/bash

if [ -z "$1" -o "$1" = "-h" -o "$1" = "-help" -o "$1" = "--help" ] ; then
	echo 'Usage: gravatar.sh someone@example.com'
	echo 'See also: http://en.gravatar.com/site/implement/images/'
	exit 1
fi

MD5=`echo -n "$1" | md5sum | sed 's/ \+- *$//'`
echo "http://www.gravatar.com/avatar/${MD5}.jpg?s=512"

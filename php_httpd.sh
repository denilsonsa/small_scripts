#!/bin/sh
#
# Problem: it can potentially run arbitrary PHP code. Be careful.

if [ "$#" = "0" ] ; then
	EXTRAS="-S 127.0.0.1:8000"
else
	EXTRAS=""
fi

echo_exec() {
	echo "$@"
	exec "$@"
}

echo_exec php ${EXTRAS} "$@"

#!/bin/sh
#
# Problem: it doesn't serve JavaScript with the correct MIME type, thus
# browsers refuse to run JavaScript.

HAS_PORT=0

for p in "$@" ; do
	case "${p}" in
		-p*)
			HAS_PORT=1
			break
			;;
	esac
done

if [ "${HAS_PORT}" = "0" ] ; then
	EXTRAS="-p 8000"
else
	EXTRAS=""
fi

echo_exec() {
	echo "$@"
	exec "$@"
}

echo_exec busybox httpd -f ${EXTRAS} "$@"

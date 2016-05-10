#!/bin/bash

SCRIPTNAME=`basename "$0"`

print_help() {
	cat << EOF
Usage: $SCRIPTNAME filename
Uses 'inotifywait' to sleep until 'filename' has been modified.

Inspired by http://superuser.com/questions/181517/how-to-execute-a-command-whenever-a-file-changes/181543#181543

TODO: rewrite this as a simple Python script, using pyinotify
EOF
}

# check dependencies
if ! type inotifywait &>/dev/null ; then
	echo "You are missing the inotifywait dependency. Install the package inotify-tools (apt-get install inotify-tools)"
	exit 1
fi

# parse_parameters:
while [[ "$1" == -* ]] ; do
	case "$1" in
		-h|-help|--help)
			print_help
			exit
			;;
		--)
			#echo "-- found"
			shift
			break
			;;
		*)
			echo "Invalid parameter: '$1'"
			exit 1
			;;
	esac
done

if [ "$#" != 1 ] ; then
	echo "Incorrect parameters. Use --help for usage instructions."
	exit 1
fi

FULLNAME="$1"
BASENAME=`basename "$FULLNAME"`
DIRNAME=`dirname "$FULLNAME"`

coproc INOTIFY {
	inotifywait -q -m -e close_write,moved_to,create ${DIRNAME} &
	trap "kill $!" 1 2 3 6 15
	wait
}

trap "kill $INOTIFY_PID" 0 1 2 3 6 15

# BUG! Não vai funcionar com arquivos contendo caracteres estranhos
sed --regexp-extended -n "/ (CLOSE_WRITE|MOVED_TO|CREATE)(,CLOSE)? ${BASENAME}\$/q" 0<&${INOTIFY[0]}

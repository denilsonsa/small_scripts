#!/bin/bash
# http://axkibe.github.io/lsyncd/faq/postscript/

/usr/bin/rsync "$@"
result=$?

(
	if [ $result -eq 0 ]; then
		# Icons that are not found on my system:
		# * sync-synchronizing
		# * sync-error
		notify-send --expire-time=3000 --category=transfer.complete --icon=folder-sync "lsyncd finished" "rsync $*"
	else
		notify-send --expire-time=9000 --category=transfer.error --icon=error "lsyncd error" "rsync $*"
	fi
) >/dev/null 2>/dev/null </dev/null

exit $result

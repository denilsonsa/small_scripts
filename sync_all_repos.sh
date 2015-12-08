#!/bin/bash
#
# When run inside a directory that contains multiple git or hg repositories,
# syncs each one of them (by calling pull followed by push).
#
# Uses ssh-agent to store the default keys, and removes those keys at the end.
# This allows typing the key passphrase only once.
#
# This script expects repos synced over SSH, or unauthenticated (download-only)
# over HTTPS.
#
# If the repos require authentication over HTTPS, then there will be a password
# prompt for each one. This will be very annoying, and it falls outside of the
# scope of this script (that means, please configure those repositories to use
# SSH instead).

# If ssh-agent is not running, restart the script inside ssh-agent.
if [ -z "${SSH_AUTH_SOCK}" ] ; then
	exec ssh-agent "$0" "$@"
	exit
fi

# Adding the default keys.
ssh-add || {
	echo "Make sure ssh-agent is running. If it is not running, clear the following vars:"
	echo unset SSH_AUTH_SOCK
	echo unset SSH_AGENT_PID
	exit 1
}

# Iterating over each directory.
for d in */ ; do

	if [ -d "$d/.git" ] ; then
		# Skipping repositories without a remote address.
		if grep -q '^[[:space:]]*\[remote' "$d/.git/config" ; then
			# Skipping pushing repositories without a username.
			grep -q '^[[:space:]]*url[[:space:]]*=[^#]\+@' "$d/.git/config"
			SHOULD_PUSH="$?"
			(
				set -x
				cd "$d"
				git pull && [ "$SHOULD_PUSH" = 0 ] && git push
			)
		fi
	fi

	if [ -d "$d/.hg" ] ; then
		# Skipping repositories without a default path.
		if grep -q '^[[:space:]]*default[[:space:]]*=' "$d/.hg/hgrc" ; then
			(
				set -x
				cd "$d"
				hg pull -u && hg push
			)
		fi
	fi

done

# Removing the keys from the agent.
ssh-add -d

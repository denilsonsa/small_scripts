#!/bin/bash

SCRIPTFILENAME=`basename "$0"`
SCRIPTNAME="$SCRIPTFILENAME version 1.0"

print_help() {
	echo "$SCRIPTNAME"
	echo "Usage: $SCRIPTFILENAME <id> [wget options]"
	echo "Where <id> is the ROM id from planetemu download page. This id can be found as"
	echo "a hidden field in HTML form named \"MyForm\", as well at end of page URL."
	echo ""
	echo "The HTML form will be POSTed using curl. The planetemu server will redirect"
	echo "the client to an FTP server, from where the client can download the file. wget"
	echo "is used to fetch the file. wget will automatically continue partially-retrieved"
	echo "downloads. (woohoo! now even dial-up users can download those huge files)"
	echo ""
	echo "This script is dumb. This script only uses one parameter. All other parameters"
	echo "are passed directly to wget. (it is useful to pass --limit-rate, for example)."
	echo ""
	echo "This script is not affiliated in any way with Planet Emulation site."
#	echo ".............................................................................."
#
# TODO:
# - Test the -L option from curl.
#
# FAQ:
#
# Q: Why do you use wget to download the FTP file, while you can use curl?
# A: curl can't handle ftp://user:pass@server/ URLs, so I need to add extra
#    code to extract user:pass info from URL to be able to use curl.
#
# Q: You should not pass user:pass info via commandline. It is unsafe. any
#    user can read this info using "ps" command.
# A: Yes, I know. In this script this is not a problem, since the username
#    and password are generated on each request, and are only valid once.
#    But I yet don't know what would be the best solution for this problem.
#    AFAIK, the script should write to ~/.netrc file, make sure it has 600
#    permissions, run wget/curl, then remove the entry from that file. (must
#    also take caution to not overwrite or delete some data hand-written by
#    user or by another program)
#
# Q: Why don't you use curl -L option?
# A: That option will follow the redirection, and it works. But curl is not
#    smart enough to save the file with the correct name, so I must filter
#    the filename from curl ouput and rename "download.php" file to the
#    correct name, or filter it and call curl again with the correct name.
#
# Q: Why need to pass -H "Expect:" to curl?
# A: Because otherwise we get "HTTP/1.1 417 Expectation Failed". See the
#    suggested solution: http://curl.haxx.se/mail/archive-2005-11/0134.html
}

get_ftp_url() {
	curl -v -H "Expect:" -A "Mozilla/4.0" -F id="$1" -F download=Telecharger --referer http://planetemu.net/ http://planetemu.net/php/roms/download.php 2>&1 | sed -n 's/[\r\n]//g;s/< Location: //p'
}

if [ -n "$1" ] && (( $1 > 0 )); then
	id="$1"
	shift

	url=`get_ftp_url $id`
	if [ -n "$url" ] ; then

		# --ftp-pasv is the default behavior for curl
#		curl -O "$url"

		wget --passive-ftp -c "$@" "$url"
	else
		echo "ERROR: Could not fetch the ftp-download URL."
		echo "(have you waited enough time before starting a new download?)"
		exit 1
	fi
else
	print_help
fi

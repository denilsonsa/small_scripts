#!/bin/bash
#
# Must be /bin/bash instead of /bin/sh because of the following bashisms:
#   $'\n'
#   $(< filename)  # instead of $(cat filename)
#   echo -E

if [ "$1" == '--help' -o "$1" == '-help' -o "$1" == '-h' ] ; then
	cat << EOF
Usage:
  ./git_version_smudge_or_clean.sh (clean|smudge) [filename]

If filename is not supplied, reads from stdin and outputs to stdout.
For convenience, if a filename is supplied, will perform the change in-place.


This script can be set as a custom filter in '.gitconfig' and used in
'.gitattributes'.


Upon smudging, it will change this line:
  FOOBAR = '\$timestamp\$'
into this line:
  FOOBAR = '\$timestamp:1234567890\$'
Upon cleaning, it will reverse the change.

Smudging an already smudged file is safe, it will just update the value between
the colon and the dollar sign.

Only the text between two dollar signs is changed. Anything outside the dollar
signs is ignored and preserved as is. This behavior makes it easy to embed the
version hash/date into a literal string in any programming language.


These marks are supported: hash, shorthash, datetime, utcdatetime, timestamp.
EOF
	exit
fi

main() {
	if [ "$1" = 'clean' ] ; then
		sed 's/\$\(hash\|shorthash\|datetime\|utcdatetime\|timestamp\)\(:[^$]*\)\?\$/$\1\$/'
	elif [ "$1" = 'smudge' ] ; then
		# Note: this only works because date is the last parameter.
		# Otherwise, the spaces in the date string would mess up this assignment.
		read HASH SHORTHASH TIMESTAMP DATETIME <<<$(git show --quiet --format=$'%H\n%h\n%ct\n%ci')
		UTCDATETIME="$(date --date="${DATETIME}" --utc --iso-8601=seconds )"

		sed '
			s/\$\(hash\)\(:[^$]*\)\?\$/$\1:'"${HASH}"'\$/;
			s/\$\(shorthash\)\(:[^$]*\)\?\$/$\1:'"${SHORTHASH}"'\$/;
			s/\$\(datetime\)\(:[^$]*\)\?\$/$\1:'"${DATETIME}"'\$/;
			s/\$\(utcdatetime\)\(:[^$]*\)\?\$/$\1:'"${UTCDATETIME}"'\$/;
			s/\$\(timestamp\)\(:[^$]*\)\?\$/$\1:'"${TIMESTAMP}"'\$/;
		'
	else
		>&2 echo 'Error: Must pass either "clean" or "smudge".'
		exit 1
	fi
}

if [ -n "$2" ] ; then
	if [ -r "$2" ] ; then
		NEWCONTENTS="$( main "$1" < "$2" )"
		ERROR=$?

		if [ "${ERROR}" != "0" ] ; then
			>&2 echo 'git_version_smudge_or_clean.sh: Error!'
			exit "${ERROR}"
		fi

		echo -E "${NEWCONTENTS}" > "$2"
	else
		echo "File not found or not readable: $2"
		exit 1
	fi
else
	main "$1"
fi

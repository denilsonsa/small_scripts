#!/bin/bash

THISSCRIPT=`basename $0`

print_help() {  # {{{
	cat << EOF
Usage: $THISSCRIPT [options] <filename.kmz> [filename.kmz... ]

This script will extract the "doc.kml" file from inside the ".kmz", and will
save it as "filename.kml" (the same name, but with .kml extension).
Note that any attached files (other than doc.kml) are just ignored.

Options:
  -f, --force                  do not prompt before overwriting
  -i, --interactive            prompt before overwrite (default)
  -v, --verbose                explain what is being done
  -h, --help                   display this help and exit
EOF
}  # }}}

process_file() {  # {{{
	KMZFILE="$1"
	KMLFILE="${KMZFILE%.kmz}.kml"

	if [[ "$FORCE" = 0 && -e "$KMLFILE" ]]; then
		while true; do
			echo -n "The file '$KMLFILE' already exists. Overwrite? [y/n] "
			read ANSWER || return 1
			case $ANSWER in
				[yY]|[yY][eE][sS])
					break
					;;
				[nN]|[nN][oO])
					return 1
					;;
			esac
		done
	fi

	[[ "$VERBOSE" = 1 ]] && echo "Extracting from '$KMZFILE' to '$KMLFILE'"
	unzip -p "$KMZFILE" doc.kml > "$KMLFILE"
}  # }}}

# Parsing parameters  {{{

FORCE=0
VERBOSE=0

while [[ $1 == -* ]] ; do
	case $1 in
		-h|-\?|-help|--help)
			print_help
			exit 0
			;;
		-f|--force)
			FORCE=1
			;;
		-i|--interactive)
			FORCE=0
			;;
		-v|--verbose)
			VERBOSE=1
			;;
		*)
			echo "$MYNAME: Invalid parameter '$1'. Use -h for usage instructions."
			exit 1
			;;
	esac
	shift
done
# }}}


if [[ $1 == "" ]] ; then
	echo "$THISSCRIPT: No input files! Use -h for usage instructions."
	exit 2
fi

while [[ -n $1 ]] ; do
	FILENAME="$1"

	if [[ ! -r "$FILENAME" ]] ; then
		echo "$THISSCRIPT: File '$FILENAME' not found or not readable."
		exit 3
	fi
	if [[ "$FILENAME" != *.kmz ]] ; then
		echo "$THISSCRIPT: File '$FILENAME' does not have '.kmz' extension."
		exit 3
	fi


	process_file "$FILENAME"

	shift
done


#!/bin/bash
#
# Easy way to convert multiple files to MP3 without having to remember cryptic
# ffmpeg parameters or how to implement a loop in shell.
#
# TODO/possible future enhancement: run the encoding in parallel, on multiple
# processes. Look at zopflipng_in_place for inspiration.

print_help() {
	cat << EOF
Usage: ${MYNAME} [parameters] [audio files...]

Parameters:
  -o, --output <dir>   Save files to <dir>. Automatically creates <dir> if it does not exist.
  -y, -f, --force      Overwrite files without asking.
  -i, --interactive    Ask before overwriting files. This is the default.
  -v, --verbose        Print additional information, useful for debugging.
  --delete             Delete original files after conversion. Warning: no confirmation is asked!

Encoding parameters:
  --cbr                Use CBR (Constant Bit Rate). This is the default.
  --vbr                Use VBR (Variable Bit Rate).
  --stereo             Save the output as stereo (two channels). This is the default.
  --mono               Save the output as mono (single-channel).
  --nocover            Remove the cover image from the output file.

Quality-related parameters:
  -b, --bitrate <br>   Use <br>kbps as the CBR bitrate. Default is 128kbps.
  -q, --quality <q>    Use <q> as the quality for VBR. Range is from 0 (better) to 9 (worst). Default is 4.
  --awful              Use 7 for VBR and 64kbps for CBR.
  --lower              Use 6 for VBR and 80kbps for CBR.
  --low                Use 5 for VBR and 96kbps for CBR.
  --medium             Use 4 for VBR and 128kbps for CBR. This is the default.
  --high               Use 3 for VBR and 160kbps for CBR.
  --higher             Use 2 for VBR and 192kbps for CBR.
EOF
}

die() {
	echo "${MYNAME}:" "$@"
	exit 1
}

parse_arguments() {
	BITRATE=128
	QUALITY=4
	USE_VBR=0
	QUALITY_PARAMS=( )

	CHANNELS=2
	COVER=( )
	AUTO_DELETE=0
	FFMPEG=''
	FILES=( )
	OVERWRITE=( )
	OUTPUT_DIR=''
	VERBOSE=0

	while [[ $# != 0 ]] ; do
		case "$1" in
			-h | -help | --help )
				print_help
				exit
				;;
			--awful  ) QUALITY=7 ; BITRATE=64 ;;
			--lower  ) QUALITY=6 ; BITRATE=80 ;;
			--low    ) QUALITY=5 ; BITRATE=96 ;;
			--medium ) QUALITY=4 ; BITRATE=128 ;;  # Default value.
			--high   ) QUALITY=3 ; BITRATE=160 ;;
			--higher ) QUALITY=2 ; BITRATE=192 ;;
			-o | --output  ) OUTPUT_DIR="$2" ; shift ;;
			-b | --bitrate ) BITRATE="$2"    ; shift ;;
			-q | --quality ) QUALITY="$2"    ; shift ;;
			--cbr    ) USE_VBR=0 ; shift ;;
			--vbr    ) USE_VBR=1 ; shift ;;
			--stereo ) CHANNELS=2 ; shift ;;
			--mono   ) CHANNELS=1 ; shift ;;
			--nocover | --no-cover ) COVER=('-vn') ;;
			-y | -f | --force  ) OVERWRITE=('-y') ;;
			-i | --interactive ) OVERWRITE=() ;;
			-v | --verbose ) VERBOSE=1 ;;
			--delete ) AUTO_DELETE=1 ;;
			-- )
				shift
				break
				;;
			* )
				FILES+=("$1")
				;;
		esac
		shift
	done
	if [[ $# != 0 ]] ; then
		FILES+=("$@")
	fi

	if [ -z "${FFMPEG}" ] ; then
		detect_ffmpeg
	fi

	if [[ "${#FILES[@]}" = 0 ]] ; then
		die "Missing parameters, use --help for instructions."
	fi

	if [ -n "${OUTPUT_DIR}" ] ; then
		if [ -e "${OUTPUT_DIR}" ] ; then
			if ! [ -d "${OUTPUT_DIR}" ] ; then
				die "Supplied output directory is not a directory: ${OUTPUT_DIR}"
			fi
		else
			[ "${VERBOSE}" = 1 ] && set -x
			mkdir -p -- "${OUTPUT_DIR}" || die "Could not create the output directory: ${OUTPUT_DIR}"
			set +x  # [ "${VERBOSE}" = 1 ]
		fi
	fi

	if [ "${USE_VBR}" = 1 ] ; then
		QUALITY_PARAMS=('-aq' "${QUALITY}")
	else
		QUALITY_PARAMS=('-ab' "${BITRATE}k")
	fi

	if [ "${VERBOSE}" = 1 ] ; then
		cat << EOF
OUTPUT_DIR=${OUTPUT_DIR}
FFMPEG=${FFMPEG}
OVERWRITE=${OVERWRITE[@]}
CHANNELS=${CHANNELS}
QUALITY=${QUALITY}
BITRATE=${BITRATE}
QUALITY_PARAMS=${QUALITY_PARAMS[@]}
COVER=${COVER[@]}
EOF
	fi
}

detect_ffmpeg() {
	FFMPEG=ffmpeg
	JOINT_STEREO=('-joint_stereo' '1')
	END_OF_PARAMS=('--')
	if ! which "${FFMPEG}" &> /dev/null ; then
		# Ubuntu 14.04 LTS
		FFMPEG=avconv
		# Not supported by avconv in Ubuntu 14.04:
		JOINT_STEREO=()
		END_OF_PARAMS=()
	fi
	if ! which "${FFMPEG}" &> /dev/null ; then
		die "Cannot find ffmpeg nor avconv. Please install one of them."
	fi
}


MYNAME=`basename "$0"`
parse_arguments "$@"

for f in "${FILES[@]}"; do

	# Putting the file in the correct directory…
	if [ -z "${OUTPUT_DIR}" ] ; then
		output="${f}"
	else
		output="${OUTPUT_DIR}/$(basename -- "${f}")"
	fi
	# …and with the correct extension.
	# https://stackoverflow.com/questions/965053/extract-filename-and-extension-in-bash
	output="${output%.*}.mp3"

	# -v or -loglevel: default is info
	# -y: overwrite output files
	# -acodec is an alias for -codec:a
	# -aq is an alias for -q:a or -qscale:a
	# -ab is an alias for -b:a
	# -ac is the number of audio channels
	# See also:
	# https://trac.ffmpeg.org/wiki/Encode/MP3
	# https://ffmpeg.org/ffmpeg.html
	# https://ffmpeg.org/ffmpeg-codecs.html#libmp3lame-1
	[ "${VERBOSE}" = 1 ] && set -x
	"${FFMPEG}" \
		-v warning \
		"${OVERWRITE[@]}" \
		-i "${f}" \
		"${COVER[@]}" \
		-acodec libmp3lame \
		-ac "${CHANNELS}" \
		"${QUALITY_PARAMS[@]}" \
		"${JOINT_STEREO[@]}" \
		"${END_OF_PARAMS[@]}" \
		"${output}" \
		&& [ "${AUTO_DELETE}" = 1 ] && rm -f -- "${f}"
	set +x  # [ "${VERBOSE}" = 1 ]
done

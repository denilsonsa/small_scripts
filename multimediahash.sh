#!/bin/bash
#
# Inspired by:
# https://www.reddit.com/r/ffmpeg/comments/wbvio2/comparing_video_files_that_are_supposed_to_be/
# https://trac.ffmpeg.org/wiki/framemd5%20Intro%20and%20HowTo
# https://stackoverflow.com/questions/63608312/how-to-md5-the-video-track-only-in-ffmpeg


print_help() {
	cat << EOF
Usage: $MYNAME [-d] [-f hashformat] audio_or_video_file(s)

This script uses ffmpeg to compute a hash of the audio/video stream of a multimedia file.

Parameters:
  -d, --decode  Fully decodes the video/audio stream. Very slow.
  -a, --audio   Only considers the audio stream.
  -v, --video   Only considers the video stream.
  -f, --format  Chooses the desired hash format. Valid formats are:
                hash, md5, crc, framehash, framemd5, framecrc, streamhash
EOF
}

parse_arguments() {
	DECODE=0
	HASH_FORMAT=hash
	ONLY_AUDIO=0
	ONLY_VIDEO=0
	FILES=( )
	DECODE_PARAMS=( -c:v copy -c:a copy )
	MAP_PARAMS=( -map '0:a?' -map '0:v?' )

	while [[ $# != 0 ]] ; do
		case "$1" in
			-h | -help | --help )
				print_help
				exit
				;;

			-d | -decode | --decode ) DECODE=1 ;;
			-a | -audio  | --audio  ) ONLY_AUDIO=1 ;;
			-v | -video  | --video  ) ONLY_VIDEO=1 ;;

			-f | -format | --format ) HASH_FORMAT="$2" ; shift ;;

			* )
				FILES+=("$1")
				;;
		esac
		shift
	done

	if [[ "${#FILES[@]}" = 0 ]] ; then
		echo "${MYNAME}: Did you forget to pass the filename? Use --help for instructions."
		exit 1
	fi

	if [[ "${DECODE}" = 1 ]] ; then
		DECODE_PARAMS=( )
	fi

	# https://ffmpeg.org/ffmpeg.html#toc-Advanced-options
	# `-map 0:a?` means:
	# → Map from the first input file (0)
	# → All audio streams (a) or all video streams (v)
	# → Ignore the mapping if there is no stream of that type (?)
	if [[ "${ONLY_AUDIO}" = 1 || "${ONLY_VIDEO}" = 1 ]] ; then
		MAP_PARAMS=( )
	fi
	if [[ "${ONLY_AUDIO}" = 1 ]] ; then
		MAP_PARAMS+=( -map '0:a' )
	fi
	if [[ "${ONLY_VIDEO}" = 1 ]] ; then
		MAP_PARAMS+=( -map '0:v' )
	fi
}


MYNAME=`basename "$0"`
parse_arguments "$@"

# Exit this script early upon receiving Ctrl+C.
# Without this, `ffmpeg` would handle the Ctrl+C and the loop would continue with the next file.
trap 'exit' 2

for filename in "${FILES[@]}" ; do
	echo -nE "${filename}" $'\t'
	ffmpeg -nostdin -hide_banner -loglevel error -i "${filename}" "${MAP_PARAMS[@]}" "${DECODE_PARAMS[@]}" -f "${HASH_FORMAT}" -
done

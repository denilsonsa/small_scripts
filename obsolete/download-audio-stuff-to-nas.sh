#!/bin/sh
#
# Trivial wrapper script around:
# https://github.com/xtream1101/humblebundle-downloader
# https://pypi.org/project/humblebundle-downloader/

if [ -z "$1" ] ; then
  echo "Please run: $0 'VALUE_OF_simpleauth_sess_COOKIE'"
  echo "See also: https://github.com/xtream1101/humblebundle-downloader"
  exit
fi

exec ./venv/bin/hbd --progress --update --session-auth "$1" --library-path /mnt/foobar/HumbleBundleAudio/ --platform audio

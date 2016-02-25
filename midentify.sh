#!/bin/sh
# Inspired by:
# https://github.com/larsmagne/mplayer/blob/master/TOOLS/midentify.sh

mplayer -noconfig all -cache-min 0 -vo null -ao null -frames 0 -identify "$@"

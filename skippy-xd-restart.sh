#!/bin/sh

killall skippy-xd
rm -f /tmp/skippy-xd-fifo
skippy-xd --start-daemon &

#!/bin/bash
#
# Ad-hoc system stats monitor that prints values periodically on each line.
# This bash version is pretty limited, please consider using the Perl version,
# as it works much better. Look for `dumb_monitor.pl`.

while sleep 30 ; do
	echo \
		`date` \
		$'\tTemp:' \
		`cat /sys/class/thermal/thermal_zone0/temp` \
		$'mC°' \
		$'\tLoadavg:' \
		`cat /proc/loadavg` \
		$'\tCPU clock:' \
		`cat /sys/devices/system/cpu/cpu?/cpufreq/scaling_cur_freq` \
		$'kHz' \

done

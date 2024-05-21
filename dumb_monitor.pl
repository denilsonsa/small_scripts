#!/usr/bin/env perl
#
# Ad-hoc system stats monitor that prints values periodically on each line.

use strict;
use warnings;

use POSIX qw(strftime);

# This is easy to use:
#     use File::Slurp qw(read_file);
# But instead I'm rewriting it here to have zero dependencies.
sub slurp {
	my $filename = shift;
	open(my $fh, '<', $filename) or die "Error openting $filename: $!";
	local $/;  # slurp mode
	my $data = <$fh>;
	close($fh);
	$data =~ s/^\s*//;
	$data =~ s/\s*$//;
	return $data;
}

my $sleep_delay_seconds = $ARGV[0] || 30;

while (1) {
	# Raw data is in milliCelsius.
	my $temp = slurp('/sys/class/thermal/thermal_zone0/temp') / 1000;

	# We have from cpu0 to cpu4, but I believe all of them follow the same clock.
	# Raaw data is in kHz.
	my $clock = slurp('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq') / 1000;

	my @loadavg = split(/\s+/, slurp('/proc/loadavg'));
	# ignoring the 5th item: last PID used
	my ($one, $five, $ten, $processes, undef) = @loadavg;

	# TODO: Also read from /proc/meminfo

	# TODO: Also detect rpi_volt:
	# /sys/class/hwmon/hwmon*/
	# https://github.com/custom-components/sensor.rpi_power/blob/master/custom_components/rpi_power/sensor.py

	my $now = strftime("%Y-%m-%d %H:%M:%S", localtime);

	printf(
		"%s  %4.1f°C  %4.0fMHz  Load: %s %s %s  Processes: %s\n",
		$now,
		$temp,
		$clock,
		$one,
		$five,
		$ten,
		$processes,
	);
	sleep $sleep_delay_seconds;
}

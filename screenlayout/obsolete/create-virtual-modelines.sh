#!/bin/sh

add_modeline() {
	local modeline name
	modeline="$(gtf "$2" "$3" "$4" | sed -n 's/.*Modeline "\([^" ]\+\)" \(.*\)/\1 \2/p')"
	name="$(echo "${modeline}" | sed 's/\([^ ]\+\) .*/\1/')"
	if [ -z "${modeline}" -o -z "${name}" ] ; then
		echo "Error! modeline='${modeline}' name='${name}'"
		exit 1
	fi
	xrandr --delmode "$1" "${name}"
	xrandr --rmmode "${name}"
	xrandr --newmode ${modeline}
	xrandr --addmode "$1" "${name}"
}

add_modeline VIRTUAL-1 1920 1080 60
add_modeline VIRTUAL-1 1920 1000 60

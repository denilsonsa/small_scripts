#!/bin/sh

# This is a quick and dirty and very ugly script to set up an ssh tunnel to my
# home network. I use it to listen to my own music collection from my Jellyfin
# instance, without exposing it to whole Internet.

# This script has been anonymized: the usernames and the domain names are
# dummies.

# HOWTO INSTALL instructions:
# * Make several symlinks to this script:
#   ln -s ssh_tunnel_to_my_home_lan.sh xssh_tunnel_to_jellyfin.sh
#   ln -s ssh_tunnel_to_my_home_lan.sh ssh_tunnel_to_jellyfin.sh
#   ln -s ssh_tunnel_to_my_home_lan.sh ssh_tunnel_to_paperless.sh
#   ln -s ssh_tunnel_to_my_home_lan.sh ssh_tunnel_to_homeassistant.sh

SCRIPTNAME=`basename "$0"`

if [ "${SCRIPTNAME}" = "xssh_tunnel_to_jellyfin.sh" ]; then

	# Run itself inside a tiny xterm window.
	exec xterm \
		+sb +sm -u8 -lc -uc -geometry 44x2 -bw 0 \
		-bg '#101010' -fg '#00A4DC' -title 'Jellyfin @ home' \
		-xrm "xterm*iconHint: ${HOME}/stuff/jellyfin" \
		-e "${0%xssh_tunnel_to_jellyfin.sh}ssh_tunnel_to_jellyfin.sh"

elif [ "${SCRIPTNAME}" = "ssh_tunnel_to_jellyfin.sh" ]; then

	DEST='myusernam@example.com'
	if ping -n -q -c 1 192.0.2.4 &> /dev/null ; then
		# If I can ping that IP address, it means I'm directly connected to my
		# LAN. Thus, I can ssh into my own Raspberry Pi4 machine directly.
		DEST='pi4'
	fi

	# It's running on 192.0.2.15:8096 (LAN IP address) which is (or should be)
	# routable through my VPS that is connected to my LAN via VPN.
	echo 'Jellyfin @ home → http://127.0.0.1:8096/'
	exec ssh -N -L 8096:192.0.2.15:8096 "${DEST}"

elif [ "${SCRIPTNAME}" = "ssh_tunnel_to_paperless.sh" ]; then

	ssh -N -L 9493:192.0.2.10:9493 myusernam@example.com

elif [ "${SCRIPTNAME}" = "ssh_tunnel_to_homeassistant.sh" ]; then

	ssh -N -L 8123:192.0.2.10:8123 myusernam@example.com

else
	echo "Unknown script name: ${SCRIPTNAME}"
fi

#!/bin/sh

if [ -z "$1" -o "$1" = "--help" -o "$1" = "-help" -o "$1" = "-h" ]; then
	THISSCRIPT=`basename $0`
	echo "Use: $THISSCRIPT <interface|all|realip> [ --netmask|-n | --netmasknumeric|-N | --macaddress|--hwaddr|-M|-H ]"
	echo "Example: $THISSCRIPT eth0"
	echo " all    = print info from all interfaces"
	echo " realip = use external HTTP service to find the real internet IP address"
elif [ "$1" = "realip" ]; then
	# Uncomment the service you want to use
	wget -q -O - http://checkip.dyndns.org/ | sed -n 's/^.*Current IP Address: *\([0-9.]\+\).*$/\1/p'
#	wget -q -O - http://www.whatismyip.com/ | sed -n '/Your \+IP \+Is/{;s/^.*Your \+IP \+Is \+\([0-9.]\+\).*$/\1/p;q;}'
else

	# Try to locate the ifconfig command
	IFCONFIG=`which ifconfig 2>/dev/null`
	if [ ! -x "$IFCONFIG" ] ; then
		# In case ifconfig was not found in $PATH (using which), let's try manually:
		for dir in {/,/usr/{,local/}}{sbin,bin} ; do
			if [ -x "$dir/ifconfig" ] ; then
				IFCONFIG="$dir/ifconfig"
				break
			fi
		done
	fi

	if [ "$1" = "all" ]; then
		IFACE=
	else
		IFACE="$1"
	fi

	if [ "$2" = "-M" -o "$2" = "-H" -o "$2" = "--macaddress" -o "$2" = "--hwaddr" ]; then
		# This section prints MAC address
		
		$IFCONFIG $IFACE | sed -n '/HWaddr/{s/.*HWaddr \([0-9A-Fa-f:]\+\).*/\1/;p}'
	else
		# This section prints IP or IP/netmask

		LINES=`$IFCONFIG $IFACE | fgrep 'inet addr'`
		# If no line found, quit.
		if [ $? != 0 ] ; then
			exit;
		fi

		#Old script version:
		#/sbin/ifconfig $1 | sed -n '/inet addr/{;s/.*inet addr:\([0-9.]\+\).*/\1/;p;}'

		if [ "$2" = "-n" -o "$2" = "--netmask" ]; then
			echo "$LINES" | sed -n 's/.*inet addr:\([0-9.]\+\).*Mask:\([0-9.]\+\).*/\1\/\2/;p'
		elif [ "$2" = "-N" -o "$2" = "--netmasknumeric" ]; then
			echo "$LINES" | awk '{IP=gensub(/.*inet addr:([0-9.]+).*/,"\\1",""); NETMASK=gensub(/.*Mask:([0-9.]+).*/,"\\1",""); split(NETMASK,V,"."); N=0; for(i=1; i<=4; i++){ while(V[i]) { N+=V[i]%2; V[i]=int(V[i]/2); } }; print IP "/" N }'
		else
			echo "$LINES" | sed -n 's/.*inet addr:\([0-9.]\+\).*/\1/;p'
		fi
	fi
fi

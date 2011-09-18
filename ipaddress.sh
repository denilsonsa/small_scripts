#!/bin/sh
#
# Written by Denilson Figueiredo de Sa <denilsonsa@gmail.com>

THISSCRIPT=`basename $0`

print_help() {
	cat << EOF
Usage: $THISSCRIPT <interface|all|realip> [ -imnh ]
Where:
  interface  print info only from the interface passed as argument (e.g. eth0)
  all        print info from all available interfaces
  realip     use an external HTTP service to discover the external IP address

  -i         print IP address (default)
  -m         print netmask in 255.0.0.0 format
  -n         print netmask in numeric format (number of 1-bits)
  -im, -in   combination of above options, print both IP and netmask

  -h         print hardware address (MAC address)

Examples:
  $THISSCRIPT all
  $THISSCRIPT eth0 -in
  $THISSCRIPT eth1 -h
  $THISSCRIPT realip
EOF
}

if [ -z "$1" -o "$1" = "--help" -o "$1" = "-help" -o "$1" = "-h" ]; then

	print_help

elif [ "$1" = "realip" ]; then

	if [ -n "$2" ]; then
		echo "$THISSCRIPT: 'realip' pseudo-interface does not support extra options."
		exit 1
	else
		# Uncomment the service you want to use
		wget -q -O - http://checkip.dyndns.org/ | sed -n 's/^.*Current IP Address: *\([0-9.]\+\).*$/\1/p'

		# <!--Do not scrape your IP from here, go to www.whatismyip.com/faq/automation.asp for more information on our automation rules.-->
		#wget -q -O - http://www.whatismyip.com/ | sed -n '/Your \+IP \+Is/{;s/^.*Your \+IP \+Is \+\([0-9.]\+\).*$/\1/p;q;}'

		#wget -q -O - http://automation.whatismyip.com/n09230945.asp

		# Other services:
		# http://checkmyip.org/
		# http://checkmyip.com/
		# However, the next one shows the IP behind the proxy:
		# http://www.checkmyip.net/
	fi

else

	# Try to locate the ifconfig command
	IFCONFIG=`which ifconfig 2>/dev/null`
	if [ ! -x "$IFCONFIG" ] ; then
		# In case ifconfig was not found in $PATH (using which), let's try manually:

		# The following line has been pre-expanded to remove this bash-ism.
		#for dir in {/,/usr/{,local/}}{sbin,bin} ; do
		# With this pre-expanded list, this script will also work with dash.
		for dir in /sbin /bin /usr/sbin /usr/bin /usr/local/sbin /usr/local/bin ; do
			if [ -x "$dir/ifconfig" ] ; then
				IFCONFIG="$dir/ifconfig"
				break
			fi
		done
	fi
	if [ ! -x "$IFCONFIG" ]; then
		echo "$THISSCRIPT: Could not find 'ifconfig' program."
		exit 1
	fi

	if [ "$1" = "all" ]; then
		IFACE=
	else
		IFACE="$1"
	fi

	if [ "$2" = "-h" ]; then
		# This section prints MAC address
		$IFCONFIG $IFACE | sed -n '/HWaddr/{s/.*HWaddr \([0-9A-Fa-f:]\+\).*/\1/;p}'
	else
		# This section prints IP or IP/netmask or netsmask

		LINES=`$IFCONFIG $IFACE | fgrep 'inet addr'`
		# If no lines were found, quit.
		if [ $? != 0 ]; then
			exit 0
		fi

		if [ "$2" = "-im" -o "$2" = "-m" ]; then
			LINES=$(echo "$LINES" | sed -n 's/.*inet addr:\([0-9.]\+\).*Mask:\([0-9.]\+\).*/\1\/\2/;p')
			# Now LINES contains things like this: 127.0.0.1/255.0.0.0
		elif [ "$2" = "-in" -o "$2" = "-n" ]; then
			# DAMN IT... With backticks (`) this doesn't work. With $(), it does!
			# Within ``, the double backslashes are replaced by single backslashes,
			# leading to incorrect code being passed to awk.
			LINES=$(echo "$LINES" | awk '{IP=gensub(/.*inet addr:([0-9.]+).*/,"\\1",""); NETMASK=gensub(/.*Mask:([0-9.]+).*/,"\\1",""); split(NETMASK,V,"."); N=0; for(i=1; i<=4; i++){ while(V[i]) { N+=V[i]%2; V[i]=int(V[i]/2); } }; print IP "/" N }')
			# Now LINES contains things like this: 127.0.0.1/8
		fi

		if [ "$2" = "-i" -o "$2" = "" ]; then
			echo "$LINES" | sed -n 's/.*inet addr:\([0-9.]\+\).*/\1/;p'
		elif [ "$2" = "-im" -o "$2" = "-in" ]; then
			echo "$LINES"
		elif [ "$2" = "-m"  -o "$2" = "-n"  ]; then
			echo "$LINES" | sed -n 's,^.*/,,;p'
		fi

		#Ancient script version:
		#/sbin/ifconfig $1 | sed -n '/inet addr/{;s/.*inet addr:\([0-9.]\+\).*/\1/;p;}'
	fi
fi

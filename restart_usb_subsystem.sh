#!/bin/bash
#
# This cript disables and then re-enables the USB drivers.
#
# Copied from http://billauer.co.il/blog/2013/02/usb-reset-ehci-uhci-linux/

if [[ $EUID != 0 ]] ; then
  echo This must be run as root!
  exit 1
fi

for xhci in /sys/bus/pci/drivers/?hci_hcd ; do

  if ! cd "$xhci" ; then
    echo "Weird error. Failed to change directory to $xhci"
    exit 1
  fi

  echo "Resetting devices from $xhci..."

  for i in ????:??:??.? ; do
    if [[ -e "$i" ]] ; then
      echo "Unbinding $i"
      echo -n "$i" > unbind
      echo "Binding $i"
      echo -n "$i" > bind
    fi
  done
done

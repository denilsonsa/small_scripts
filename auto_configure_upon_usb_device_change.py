#!/usr/bin/env python3
#
# Based on:
# http://askubuntu.com/questions/508236/how-can-i-run-code-whenever-a-usb-device-is-unplugged-without-requiring-root/
# http://stackoverflow.com/questions/469243/how-can-i-listen-for-usb-device-inserted-events-in-linux-in-python

import functools
import os.path
import pyudev
import subprocess
import time


def main():
    BASE_PATH = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
    path = functools.partial(os.path.join, BASE_PATH)
    call = lambda x, *args: subprocess.call([path(x)] + list(args))

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')
    monitor.start()

    # Call them first:
    call('synclient_asus_x450c.sh')
    call('setxkbmap_my_preferences.sh')

    call('setxkbmap_secondary_keyboard.sh')
    call('xinput_disable_mouse_acceleration.sh')
    call('xset_my_preferences.sh')
    call('xsetwacom_my_preferences.sh', 'desktop')

    # Call these again whenever a USB device is plugged or unplugged:
    for device in iter(monitor.poll, None):
        # Wait a short amount of time to let the device get ready.
        time.sleep(0.250)

        call('setxkbmap_secondary_keyboard.sh')
        call('xinput_disable_mouse_acceleration.sh')
        call('xset_my_preferences.sh')
        call('xsetwacom_my_preferences.sh', 'desktop')


if __name__ == '__main__':
    main()

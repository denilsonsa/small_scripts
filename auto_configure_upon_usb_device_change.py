#!/usr/bin/env python3
#
# Based on:
# http://askubuntu.com/questions/508236/how-can-i-run-code-whenever-a-usb-device-is-unplugged-without-requiring-root/
# http://stackoverflow.com/questions/469243/how-can-i-listen-for-usb-device-inserted-events-in-linux-in-python
# https://pyudev.readthedocs.org/en/latest/guide.html#asynchronous-monitoring

import os.path
import pyudev
import subprocess
from threading import Timer


def main():
    BASE_PATH = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
    path = lambda x: os.path.join(BASE_PATH, os.path.expanduser(x))
    call = lambda x, *args: subprocess.call([path(x)] + list(args))


    timers = {
        'usb': None,
        'drm': None,
    }

    def reset_timer(which_one):
        if timers[which_one] is not None:
            timers[which_one].cancel()
        timers[which_one] = None


    def usb_hotplug_callback():
        call('setxkbmap_secondary_keyboard.sh')
        call('xinput_disable_mouse_acceleration.sh')
        call('xset_my_preferences.sh')
        call('xsetwacom_my_preferences.sh', 'desktop')

    def drm_hotplug_callback():
        call('~/.screenlayout/z-auto-detect-displays.sh')

    callbacks = {
        'usb': usb_hotplug_callback,
        'drm': drm_hotplug_callback,
    }


    def udev_event_received(device):
        if device.subsystem in callbacks:
            reset_timer(device.subsystem)
            t = Timer(0.5, callbacks[device.subsystem])
            timers[device.subsystem] = t
            t.start()


    # Call these first:
    call('synclient_asus_x450c.sh')
    call('setxkbmap_my_preferences.sh')
    usb_hotplug_callback()

    context = pyudev.Context()
    # USB devices:
    monitor_usb = pyudev.Monitor.from_netlink(context)
    monitor_usb.filter_by(subsystem='usb')
    observer_usb = pyudev.MonitorObserver(monitor_usb, callback=udev_event_received, daemon=False)
    # External monitors (HDMI or VGA):
    monitor_drm = pyudev.Monitor.from_netlink(context)
    monitor_drm.filter_by(subsystem='drm')
    observer_drm = pyudev.MonitorObserver(monitor_drm, callback=udev_event_received, daemon=False)

    observer_usb.start()
    observer_drm.start()

    # This will prevent the program from finishing:
    observer_usb.join()
    observer_drm.join()

    # Huh... Does not work? TODO: remove the daemon thing...
    # The program will never exit because the observer threads are non-daemon.
    # https://docs.python.org/3.5/library/threading.html#threading.Thread.daemon

if __name__ == '__main__':
    main()

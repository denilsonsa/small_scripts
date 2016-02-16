#!/usr/bin/env python3.5
#
# Based on:
# http://askubuntu.com/questions/508236/how-can-i-run-code-whenever-a-usb-device-is-unplugged-without-requiring-root/
# http://stackoverflow.com/questions/469243/how-can-i-listen-for-usb-device-inserted-events-in-linux-in-python
# https://pyudev.readthedocs.org/en/latest/guide.html#asynchronous-monitoring
#
#
# Troubleshooting:
#
# Problem: The script aborts after waking the laptop from sleep with the following error:
#
# Exception in thread Thread-2:
# Traceback (most recent call last):
#   File "/usr/lib/python3.4/threading.py", line 920, in _bootstrap_inner
#     self.run()
#   File "/usr/lib/python3/dist-packages/pyudev/monitor.py", line 506, in run
#     for fd, _ in notifier.poll():
# InterruptedError: [Errno 4] Interrupted system call
#
# Exception in thread Thread-1:
# Traceback (most recent call last):
#   File "/usr/lib/python3.4/threading.py", line 920, in _bootstrap_inner
#     self.run()
#   File "/usr/lib/python3/dist-packages/pyudev/monitor.py", line 506, in run
#     for fd, _ in notifier.poll():
# InterruptedError: [Errno 4] Interrupted system call
#
# Cause/solutions:
#
# * Update pyudev to version 0.17 (Aug 26, 2015) or later.
#     * https://github.com/pyudev/pyudev/commit/9dbcbf598f5eb77d8972e8d4e368e2fd1afecda8
#     * Ubuntu 15.10 (wily) still has version 0.16.
#     * Ubuntu xenial doesn't seem to update the version, yet.
#     * http://packages.ubuntu.com/search?keywords=python-pyudev
# * Update Python to 3.5 or later.
#     * https://docs.python.org/3/whatsnew/3.5.html#pep-475-retry-system-calls-failing-with-eintr
#     * Ubuntu 15.10 (wily) has Python 3.5, although it is not the default interpreter.


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
    timeouts = {
        'usb': 0.5,
        'drm': 1,
    }


    def udev_event_received(device):
        if device.subsystem in callbacks:
            reset_timer(device.subsystem)
            t = Timer(timeouts[device.subsystem], callbacks[device.subsystem])
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

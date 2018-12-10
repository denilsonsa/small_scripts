#!/usr/bin/env python3
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


class SubsystemMonitor:
    def __init__(self, subsystem, callback, wait_seconds):
        self.subsystem = subsystem  # String
        self.callback = callback
        self.wait_seconds = wait_seconds
        self.timer = None  # Timer object
        self.monitor = None  # pyudev.Monitor object
        self.observer = None  # pyudev.MonitorObserver object

    def reset_timer(self):
        if self.timer is not None:
            self.timer.cancel()
        self.timer = None

    def start_timer(self):
        self.reset_timer()
        self.timer = Timer(self.wait_seconds, self.callback)
        self.timer.start()

    def handle_device_notification(self, device):
        self.start_timer()


def init_monitors():
    '''Returns a dict that maps a subsystem to a SubsystemMonitor object.
    '''
    # Utility functions.
    BASE_PATH = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
    path = lambda x: os.path.join(BASE_PATH, os.path.expanduser(x))
    call = lambda x, *args: subprocess.call([path(x)] + list(args))

    # Runs on USB and Bluetooth events.
    def usb_hotplug_callback():
        call('xinput_disable_mouse_acceleration.sh')
        call('xmodmap_corsair_mouse_buttons.sh')
        call('setxkbmap_my_preferences.sh')
        call('xset_my_preferences.sh')
        # call('setxkbmap_secondary_keyboard.sh')
        call('setxkbmap_apple_keyboard.sh')
        call('xsetwacom_my_preferences.sh', 'desktop')

    # Runs on display events.
    def drm_hotplug_callback():
        call('~/.screenlayout/z-auto-detect-displays.sh')

    # Runs only once, when this script is started.
    def startup_callback():
        call('synclient_asus_x450c.sh')
        call('synclient_dell_e7270.sh')
        usb_hotplug_callback()
        drm_hotplug_callback()

    # Initializing the monitors.
    monitors = [
        SubsystemMonitor('__start__', startup_callback    , 0.0),
        SubsystemMonitor('usb'      , usb_hotplug_callback, 0.5),
        SubsystemMonitor('bluetooth', usb_hotplug_callback, 0.5),
        SubsystemMonitor('drm'      , drm_hotplug_callback, 1.0),
    ]

    monitor_by_subsystem = {m.subsystem: m for m in monitors}
    return monitor_by_subsystem


def main():
    monitor_by_subsystem = init_monitors()

    # Handling fake startup event.
    startup = monitor_by_subsystem.pop('__start__', None)
    if startup:
        startup.handle_device_notification(None)

    # Setting up pyudev monitors and observers.
    context = pyudev.Context()
    for m in monitor_by_subsystem.values():
        m.monitor = pyudev.Monitor.from_netlink(context)
        m.monitor.filter_by(subsystem=m.subsystem)
        m.observer = pyudev.MonitorObserver(
            m.monitor, callback=m.handle_device_notification, daemon=False)

    for m in monitor_by_subsystem.values():
        m.observer.start()

    # This will prevent the program from finishing:
    for m in monitor_by_subsystem.values():
        m.observer.join()

    # Huh... Does not work? TODO: remove the daemon thing...
    # The program will never exit because the observer threads are non-daemon.
    # https://docs.python.org/3.5/library/threading.html#threading.Thread.daemon

if __name__ == '__main__':
    main()

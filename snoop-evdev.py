#!/usr/bin/python3
"""
snoop-evdev - listen to evdev events for the specified device
==============================================================

Lists the device capabilities and events

Usage:
======

    python3 snoop-evdev.py [-c] /dev/input/event<N>

Optional Arguments
------------------

    -c           List capabilities and exit

Credits
=======
Based on https://python-evdev.readthedocs.io/en/latest/tutorial.html

"""
import sys
import time

from evdev import InputDevice, categorize, ecodes, resolve_ecodes


def main():

    dev = InputDevice(sys.argv[-1])
    print(ecodes.BTN[ecodes.BTN_MIDDLE])
    print(dev)
    print("Begin capabilities")
    for key, item in dev.capabilities(verbose=True).items():
        print(key)
        for ev in item:
            print(f"    {ev}")
    print("End capabilities")
    if '-c' in sys.argv:
        print("Exiting: -c = capabilities only")
        sys.exit(0)

    start_time = time.time_ns()
    for event in dev.read_loop():
        now = time.time_ns()
        print(f"@{(now - start_time) / 1_000_000_000:.3f} sec: {categorize(event)} => {event.value}")


if __name__ == '__main__':
    main()
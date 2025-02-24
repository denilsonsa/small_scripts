#!/bin/env python3
#
# This script is inspired by https://unix.stackexchange.com/a/593779
# Official documentation: https://docs.kde.org/stable5/en/konsole/konsole/command-line-options.html

# source location:
# https://github.com/denilsonsa/small_scripts/blob/master/konsole_snapshot.py

import argparse
import datetime
import dbus  # ← pip install dbus-python
import json
import os
import re
import subprocess
import tempfile
import time
from xml.etree import ElementTree


# Global variable for debugging statements.
VERBOSE = False


############################################################
# Convenience functions


def DEBUG(prefix, *args):
    """Debug-printing function.

    Prints a prefix message (in bold), followed by the string representation of
    all the remaining arguments. But only prints if VERBOSE is enabled.
    """
    if VERBOSE:
        print(
            ("\033[1m" + prefix + "\033[m " if prefix else "")
            + " ".join(str(x) for x in args)
        )


def xdg_config_dir():
    """Returns the configuration directory."""
    return os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")


def config_filename():
    """Returns the default configuration filename."""
    return os.path.join(xdg_config_dir(), "konsole_snapshot")


def get_bus():
    """Returns a session bus to dbus.

    Maybe in the future we want to allow using the SystemBus, or some other bus
    specified on the commandline.
    """
    return dbus.SessionBus()


def get_cwd_by_pid(pid):
    """Returns the workdir of a process.

    This works fine on Linux. It needs to be rewritten for other OSes.
    In such case, it's certainly better to just use the `psutil` Python module.
    """
    return os.readlink("/proc/{}/cwd".format(pid))


############################################################
# Functions related to saving the Konsole state


def list_children(bus, service, path):
    """Lists the children of a certain dbus node.

    Dbus is complicated. We need to call Introspect and parse the returned XML
    document.
    """
    proxy = bus.get_object(service, path)
    xml = proxy.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable")
    root = ElementTree.fromstring(xml)
    for child in root:
        if child.tag == "node":
            name = child.attrib["name"]
            if name:
                # yield (path, name)
                yield name


def get_konsoles_snapshot():
    """Get a snapshot of the current Konsole state.

    Returns a JSON-like structure with a snapshot of the currently open Konsole
    processes, windows and sessions.
    """
    # Get the list of open konsole services/processes.
    bus = get_bus()
    services = sorted(
        str(s) for s in bus.list_names() if str(s).startswith("org.kde.konsole-")
    )
    DEBUG("dbus services", services)

    saved_windows = []

    # Each service is its own Konsole instance.
    # Each time you run `konsole`, it creates a new instance.
    for service in services:
        service_id = service.replace("org.kde.konsole-", "")
        # Each instance can have multiple windows.
        # Windows can be created through File → New Window.
        windows = sorted(list_children(bus, service, "/Windows"))
        DEBUG(service + " /Windows children", windows)
        for window in windows:
            winproxy = bus.get_object(service, "/Windows/" + window)
            # Each window can have multiple tabs, or sessions.
            # We do not sort the list of sessions to preserve the tab order.
            sessions = [
                str(s)
                for s in winproxy.sessionList(dbus_interface="org.kde.konsole.Window")
            ]
            DEBUG("service {} window {} sessions".format(service_id, window), sessions)
            DEBUG(
                "\t".join(
                    ["service", "window", "session", "profile", "pid", "fg pid", "cwd"]
                )
            )
            saved_tabs = []
            for session in sessions:
                sesproxy = bus.get_object(service, "/Sessions/" + session)
                # Creating an interface just for convenience.
                # It's not needed when calling only a single method:
                # It's easier to pass dbus_interface parameter for a single use.
                sesinterface = dbus.Interface(sesproxy, "org.kde.konsole.Session")
                profile = str(sesinterface.profile())
                fg_pid = str(sesinterface.foregroundProcessId())
                pid = str(sesinterface.processId())
                cwd = get_cwd_by_pid(pid)

                # Saving the title is complicated.
                # Because it is impossible to know if the tab title was
                # modified from the default. And because Konsole has two
                # title formats: one for local and one for remote.
                # But --tabs-from-file only supports one title.
                # So, I'll give up for now. I don't use custom titles anyway.
                #
                # probably_profile_name = sesinterface.title(0)
                title_right_now = sesinterface.title(1)
                # tab_title_format = sesinterface.tabTitleFormat(0)
                # remote_title_format = sesinterface.tabTitleFormat(1)

                # fix profile to contain somehting if it is empty.. otherwise the loading fails...
                if profile is "":
                    profile = "-"

                DEBUG(
                    "",
                    "\t".join(
                        [
                            service_id,
                            window,
                            session,
                            profile,
                            pid,
                            fg_pid if fg_pid != pid else "(same)",
                            cwd,
                        ]
                    ),
                )

                # https://docs.kde.org/stable5/en/konsole/konsole/command-line-options.html
                # --tabs-from-file supports: title, workdir, profile, command
                # Out of these...
                # - `title` is troublesome to save,
                # - `command` seems less useful and more dangerous.
                # Thus, I've decided to only save the profile and the workdir.
                saved_tabs.append(
                    {
                        "title": title_right_now,
                        "profile": profile,
                        "workdir": cwd,
                    }
                )

            saved_windows.append(
                {
                    "workdir": get_cwd_by_pid(service_id),
                    "tabs": saved_tabs,
                }
            )

    DEBUG("Final snapshot", json.dumps(saved_windows, indent="  ", sort_keys=True))
    return saved_windows


def save_snapshot_to_config(snapshot, filename):
    """Saves a JSON-like snapshot to a JSON file."""
    DEBUG("Config file", filename)
    with open(filename, "w") as f:
        json.dump(
            {
                "version": 1,
                "datetime": datetime.datetime.now().isoformat(timespec="seconds"),
                "windows_and_tabs": snapshot,
            },
            f,
            indent="\t",
            sort_keys=True,
        )


############################################################
# Functions related to loading the Konsole state


def load_snapshot(filename):
    """Loads a Konsole snapshot from a JSON file.

    Gracefully returns None if the file is not found.
    Thus, it's possible to run this script to load a new snapshot even before
    saving one, without receiving any errors.
    """
    DEBUG("Config file", filename)
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def validate_tabsfromfile_field(tab, snapshot_name, field_name):
    """Validate the entries from the saved JSON.

    Konsole's --tabs-from-file parameter has a very specific and very limited
    syntax. This function tries to avoid substrings that would break the file.

    Parameters:
    - tab is a dict from the JSON snapshot.
    - snapshot_name is the name of the attribute in the JSON snapshot.
    - field_name is the name in the Konsole's tabsfromfile.
    """
    value = tab.get(snapshot_name, None)
    
    # fix profile to contain somehting if it is empty.. otherwise the loading fails...
    if field_name is "profile" and value is "":
        value = "-"

    if value:
        if ";;" in value:
            raise ValueError(
                'The string ";;" cannot be present inside {}'.format(snapshot_name)
            )
        if "\n" in value:
            raise ValueError(
                "There should be no newlines inside {}".format(snapshot_name)
            )
        return "{}: {}".format(field_name, value)
    else:
        return None


def build_tabsfromfile(tabs):
    """Builds a string in the format expected by Konsole's --tabs-from-file."""
    lines = []
    for tab in tabs:
        fields = [
            validate_tabsfromfile_field(tab, "title", "title"),
            validate_tabsfromfile_field(tab, "profile", "profile"),
            validate_tabsfromfile_field(tab, "workdir", "workdir"),
        ]
        fields = [x for x in fields if x]
        if len(fields) > 0:
            lines.append(" ;; ".join(fields))
    return "\n".join(lines)


def launch_konsoles(saved_snapshot):
    """Launches one or multiple Konsole processes.

    Given a JSON-like object representing the Konsole snapshot, this function
    will launch multiple processes, one for each window, restoring the tabs of
    each window.
    """
    # Gracefully do nothing if the file does not exist.
    if saved_snapshot is None:
        DEBUG("Do nothing, file not found.")
        return

    # Make sure we are using the same file format.
    assert saved_snapshot["version"] == 1

    # If we let Python delete the temporary file automatically,
    # the file will be deleted before Konsole has a change to read it.
    # Thus, I'm collecting all the files here to be deleted after a delay.
    tmpfiles = []
    pids = []

    try:
        for window in saved_snapshot["windows_and_tabs"]:
            cwd = window.get("workdir", ".")
            s = build_tabsfromfile(window.get("tabs", []))
            DEBUG("tabs-from-file", "\n" + s)
            with tempfile.NamedTemporaryFile("w", delete=False) as f:
                tmpfiles.append(f)
                DEBUG("Temporary file", f.name)
                f.write(s)

            # https://docs.kde.org/stable5/en/konsole/konsole/command-line-options.html
            cmdline = [
                "konsole",
                "--workdir",
                cwd,
                "--tabs-from-file",
                f.name,
                # Let's run a dummy command at the end.
                # Otherwise, Konsole will load all the saved tabs,
                # plus a new one for a new shell.
                "-e",
                "/bin/true",
            ]
            DEBUG("Launching", cmdline)
            p = subprocess.Popen(cmdline, cwd=cwd)
            pids.append(p.pid)

        # Querying dbus, waiting for the Konsole processes to finish launching.
        DEBUG("Waiting until Konsole is ready")
        bus = get_bus()
        time.sleep(0.5)
        for i in range(10000):
            try:
                proxies = [
                    bus.get_object("org.kde.konsole-{}".format(pid), "/Windows/1")
                    for pid in pids
                ]
                DEBUG("proxies", proxies)
                sessions = [
                    winproxy.sessionList(dbus_interface="org.kde.konsole.Window")
                    for winproxy in proxies
                ]
                # It seems sessionList() only returns after Konsole has finished launching.
                # Anyway, to be on the safe side, I'm doing one additional check:
                DEBUG("sessions", sessions)
                if all(len(x) > 0 for x in sessions):
                    break
            except dbus.exceptions.DBusException:
                DEBUG("Konsole not ready, querying dbus again")
                time.sleep(0.5)
    finally:
        # Deleting all the temporary files only after all Konsole processes
        # have finished launching.
        for f in tmpfiles:
            DEBUG("Deleting temporary file", f.name)
            os.remove(f.name)


############################################################
# Main functions


def parse_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Saves or loads a snapshot of the current Konsole sessions.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument(
        "-f",
        "--file",
        action="store",
        default=config_filename(),
        help="Specify a different file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print additional debugging messages",
    )
    group.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="Save a Konsole snapshot to a file",
    )
    group.add_argument(
        "-l",
        "--load",
        action="store_true",
        help="Load a Konsole snapshot from a file",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    if args.verbose:
        global VERBOSE
        VERBOSE = True

    DEBUG("Arguments", args)

    # Main logic.
    if args.save:
        save_snapshot_to_config(get_konsoles_snapshot(), args.file)
    elif args.load:
        launch_konsoles(load_snapshot(args.file))


if __name__ == "__main__":
    main()

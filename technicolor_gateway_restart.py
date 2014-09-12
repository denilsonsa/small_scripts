#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import argparse
import requests
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description='Restart the Technicolor TG580v2 modem/router',
        epilog='Note that this script automatically reads authentication'
        ' credentials from ~/.netrc, so there is no need to pass'
        ' username/password at the command-line.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        dest='force',
        help='Do not ask for confirmation, restart right away'
    )
    parser.add_argument(
        '-H', '--host', '--hostname',
        action='store',
        default='dsldevice.lan',
        type=str,
        dest='hostname',
        help='The hostname or IP address for the modem'
    )
    parser.add_argument(
        '-u', '-U', '--user', '--username',
        action='store',
        default='',
        type=str,
        dest='username',
        help='Username for HTTP authentication'
    )
    parser.add_argument(
        '-p', '-P', '--pass', '--password',
        action='store',
        default='',
        type=str,
        dest='password',
        help='Password for HTTP authentication'
    )
    options = parser.parse_args()
    return options


def restart_modem(hostname='dsldevice.lan', username='', password=''):
    url = 'http://{0}/cgi-bin/restart.exe'.format(hostname)
    referer = 'http://{0}/sys_boot.htm'.format(hostname)
    # Explicit auth is not required, because the library can already read from
    # ~/.netrc.
    auth = (username, password) if username or password else None

    # For some weird reason, the first request always returns 401 Unauthorized.
    # Retrying will work, and it will continue working for a couple of minutes.
    for i in range(2):
        r = requests.post(url, auth=auth, headers={
            'Referer': referer
        })
        # If it returns 401, let's try once more.
        if r.status_code != 401:
            break

    r.raise_for_status()
    return r.text


def main():
    options = parse_args()

    if not options.force:
        # This link provides a more complete implementation of a prompt:
        # http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
        answer = input('Restart modem at http://{0}/ ? [y/N] '.format(
            options.hostname))
        answer = answer.strip().lower()
        if answer not in ['y', 'yes', 'yeah', 'yep']:
            print('Aborting.')
            sys.exit(1)

    try:
        restart_modem(hostname=options.hostname,
            username=options.username, password=options.password)
    except requests.exceptions.HTTPError as e:
        print(e.response.url)
        print(e)
        sys.exit(1)

if __name__ == '__main__':
    main()

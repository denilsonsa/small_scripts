#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import argparse
import requests
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description='Disconnects and reconnects the WAN of TP-LINK TL-WR842ND router (useful when using PPPoE)',
        epilog='Note that this script automatically reads authentication'
        ' credentials from ~/.netrc, so there is no need to pass'
        ' username/password at the command-line.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        dest='force',
        help='Do not ask for confirmation, reconnect right away'
    )
    parser.add_argument(
        '-H', '--host', '--hostname',
        action='store',
        default='tplinklogin.net',
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


def reconnect_wan(hostname='dsldevice.lan', username='', password=''):
    # Explicit auth is not required, because the library can already read from
    # ~/.netrc.
    auth = (username, password) if username or password else None

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=1)
    session.mount('http://', adapter)

    for url in [
        'http://{0}/userRpm/StatusRpm.htm?Disconnect=Disconnect&wan=1'.format(hostname),
        'http://{0}/userRpm/StatusRpm.htm?Connect=Connect&wan=1'.format(hostname),
    ]:
        r = session.get(url, auth=auth)
        r.raise_for_status()


def main():
    options = parse_args()

    if not options.force:
        # This link provides a more complete implementation of a prompt:
        # http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
        answer = input('Reconnect WAN at http://{0}/ ? [y/N] '.format(
            options.hostname))
        answer = answer.strip().lower()
        if answer not in ['y', 'yes', 'yeah', 'yep']:
            print('Aborting.')
            sys.exit(1)

    try:
        reconnect_wan(
            hostname=options.hostname,
            username=options.username,
            password=options.password
        )
    except requests.exceptions.HTTPError as e:
        print(e.response.url)
        print(e)
        sys.exit(1)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# Inspired by this question:
# https://stackoverflow.com/questions/24481564/
#
# Why is it so hard to find a good documentation of the available API endpoints
# and API versions?

import argparse
import os.path
import re
import sys
from collections import defaultdict

try:
    import requests
except ImportError:
    print("Please install the 'requests' module.")
    print("  sudo apt-get install python3-requests")
    print("  pip install requests")
    print("  http://docs.python-requests.org/")
    raise


URL_BASE = 'https://registry.hub.docker.com/'
USER_AGENT = 'docker_remote_tags.py <https://bitbucket.org/denilsonsa/small_scripts/src/default/docker_remote_tags.py>'

# Quick and dirty implementation of a subset of OAuth 2.
# A much better idea would be to use requests_oauthlib,
# which in turn depends on oauthlib.
# * <https://github.com/requests/requests-oauthlib/>
# * <https://github.com/idan/oauthlib>
# But I wanted to keep the dependencies to a minimum.
TOKEN = None


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Lists all tags for a docker image from Docker Hub.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'imagename',
        nargs='+',
        help='Image name, such as "alpine" or "phusion/baseimage"'
    )
    args = parser.parse_args()
    return args


# Quick and dirty convenience function.
def GET(endpoint):
    headers = {
        'User-Agent': USER_AGENT,
    }

    if endpoint.startswith('http'):
        url = endpoint
    else:
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        url = os.path.join(URL_BASE, endpoint)
        if TOKEN is not None:
            headers['Authorization'] = 'Bearer ' + TOKEN

    return requests.get(url, headers=headers)


# Tries a request using the previously saved TOKEN.
# If it fails with 401 code, tries to get a new token and retries the request.
def dirty_oauth2_get(endpoint):
    resp = GET(endpoint)
    if resp.status_code == 200:
        return resp
    elif resp.status_code == 401:
        global TOKEN
        auth = resp.headers['Www-Authenticate']
        if auth.startswith('Bearer '):
            realm = re.search('realm="([^"]+)"', auth).group(1)
            assert realm.startswith('https')

            service = re.search('service="([^"]+)"', auth).group(1)

            scope_match = re.search('scope="([^"]+)"', auth)
            scope = scope_match.group(1) if scope_match else ''

            authresp = GET(realm + '?service=' + service + '&scope=' + scope)
            authresp.raise_for_status()
            assert authresp.status_code == 200

            TOKEN = authresp.json()['token']
        elif auth.startswith('JWT '):
            TOKEN = None

        # Second try, it should work now.
        second = GET(endpoint)
        second.raise_for_status()
        assert second.status_code == 200
        #assert second.headers['Docker-Distribution-API-Version'] == 'registry/2.0'
        return second
    else:
        resp.raise_for_status()


def get_tags_for_image(image):
    if '/' not in image:
        image = 'library/' + image

    if False:
        # Lists just the tag names, and nothing else.
        # https://docs.docker.com/registry/spec/api/#listing-image-tags
        dirty_oauth2_get('v2/{0}/tags/list/'.format(image))

    if False:
        # List the tags and some extra information.
        # {"full_size": 25225569,
        #  "name": "3.4-alpine",
        #  "v2": True,
        #  "id": 1763076,
        #  "last_updater": 2215,
        #  "image_id": None,
        #  "last_updated": "2016-03-19T02:30:38.100251Z",
        #  "creator": 2215,
        #  "repository": 26870},
        page = 1
        tags = []
        while True:
            resp = dirty_oauth2_get('v2/repositories/{0}/tags/?page={1}'.format(image, page))
            j = resp.json()

            tags.extend(j['results'])

            if j.get('next', None) is None:
                break
            else:
                page += 1

        return tags

    if True:
        # Returns a list of:
        # {"layer": "1f87baec",
        #  "name": "latest"},
        # With this, I can aggregate tags that point to the same version!
        # Why can't I do the same in the other API endpoints?
        # Where is the documentation?
        resp = dirty_oauth2_get('v1/repositories/{0}/tags'.format(image))
        d = defaultdict(list)
        for tag in resp.json():
            layer = tag['layer']
            name = tag['name']
            d[layer].append(name)

        for tags in d.values():
            tags.sort()

        for layer, tags in sorted(d.items(), key=lambda x: x[1]):
            print('{0}: {1}'.format(
                layer,
                ', '.join(tags)
            ))


def main():
    options = parse_arguments()

    for image in options.imagename:
        get_tags_for_image(image)


if __name__ == '__main__':
    main()

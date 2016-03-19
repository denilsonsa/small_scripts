#!/bin/bash
# Returns the tags for a given docker image.
# Based on http://stackoverflow.com/a/32622147/

print_help_and_exit() {
	name=`basename "$0"`
	echo "Usage:"
	echo "  ${name} alpine"
	echo "  ${name} phusion/baseimage"
	exit
}

repo="$1"

[ "$#" != 1  ] && print_help_and_exit
[ "$" = "-h" ] && print_help_and_exit
[ "$" = "-help" ] && print_help_and_exit
[ "$" = "--help" ] && print_help_and_exit

if [[ "${repo}" != */* ]]; then
	repo="library/${repo}"
fi

# v2 API does not list all tags at once, it seems to use some kind of pagination.
#url="https://registry.hub.docker.com/v2/repositories/${repo}/tags/"
##echo "${url}"
#curl -s -S "${url}" | jq '."results"[]["name"]' | sort

# v1 API lists everything in a single request.
url="https://registry.hub.docker.com/v1/repositories/${repo}/tags"
#echo "${url}"
curl -s -S "${url}" | jq '.[]["name"]' | sed 's/^"\(.*\)"$/\1/' | sort

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# produce all url links
#
def get_urls(url_rules, releases, members):
    urls = []

    url_rule = url_rules["MyAssignments"]
    for release in releases:
        for member in members:
            urls.append(get_url(url_rule, release, member))

    return urls

#
# produce one url
#
def get_url(url_rule, release, member):

    url = ""

    for element in url_rule:
        if element == "$stream":
            url += release["stream"]
        elif element == "$version":
            url += release["version"]
        elif element == "$id":
            url += member["id"]
        else:
            url += element

    return url

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# produce all url links
#
def get_urls(url_rule, releases, members):
    urls = []
    for release in releases.values():
        for member in members.values():
            urls.append(get_url(url_rule, release, member))
    return urls

#
# returns a dictionary mapping member/release to url
# i.e., urlsDict[member["id"]][release["stream"]] to get the url
#
def get_urlsDict(url_rule, releases, members):
    urlsDict = {}
    for member in members.values():
        urlsDict[member["id"]] = {}
        for release in releases.values():
            urlsDict[member["id"]][release["stream"]] = get_url(url_rule, release, member)
    return urlsDict

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

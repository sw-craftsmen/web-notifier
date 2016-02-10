#!/usr/bin/env python3
# -*- coding: utf-8 -*-

DEFAULT_URL_RULES_FILE = "url_gen/url.json"

#
# produce all url links
#
def get_urls(releases, members):
    import json
    url_rules_file = DEFAULT_URL_RULES_FILE
    urls = []

    print("url rules file:", url_rules_file)
    with open(url_rules_file) as url_rules_fp:
        url_rules = json.load(url_rules_fp)

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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy


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


class UrlGenerator(object):
    def __init__(self, config_data):
        assert config_data
        self.__config_data = config_data
        # initialize release["stream"]
        for key, release in self.__config_data["releases"].items():
            release["stream"] = key
        # initialize member["id"]
        for key, member in self.__config_data["members"].items():
            member["id"] = key
        self.__url_and_key = self.gen()

    def __iter__(self):
        return self

    def __next__(self):
        return self.__url_and_key.__next__()

    def gen(self):
        releases = self.__config_data["releases"]
        members = self.__config_data["members"]
        url_rules = self.__config_data["urlRules"]

        url_rule = url_rules["MyAssignments"]
        urlsDict = get_urlsDict(url_rule, releases, members)
        url_and_key = []
        for member in members.values():
            member_id = member["id"]
            key = {"member_id": member_id}

            for release in releases.values():
                release_stream = release["stream"]
                key["release_stream"] = release_stream
                url_and_key.append([urlsDict[member_id][release_stream], copy.deepcopy(key)])
        return iter(url_and_key)


if __name__ == '__main__':
    config_file = "../config.json"
    with open(config_file) as config_fp:
        import json
        config_data = json.load(config_fp)
    for url, key in UrlGenerator(config_data):
        print(url)
        print(key)

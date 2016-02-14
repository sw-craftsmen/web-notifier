#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from htm_parse.parse import get_parsed_data
from pp.pretty_print import get_beautiful_data
from url_gen.generator import UrlGenerator
from web_fetch.fetcher import get_web_content
from analyze.analyzer import get_analyzed_data
from notify.notifier import notify

DEFAULT_CONFIG_FILE = "config.json"


class WebNotifier(object):

    config_data = None

    def __init__(self):
        config_file = DEFAULT_CONFIG_FILE
        import sys
        if len(sys.argv) >= 2:
            for argument in sys.argv[1:]:
                if "-" == argument[0]:
                    if argument in ["-h", "-help"]:
                        self.__help()
                        sys.exit()
                    else:
                        print("unrecognized option:", argument)
                else:
                    config_file = argument
        self.__parse_config(config_file)

    def __parse_config(self, config_file):
        import json
        print("config file:", config_file)
        config_fp = open(config_file)
        self.config_data = json.load(config_fp)
        config_fp.close()

    def run(self):
        print("web-notifier is running!")

        parsed_data = {}

        for url, key in UrlGenerator(self.config_data):
            print("[got url]", url)

            web_content = get_web_content(url)
            print("[got web content]")

            parsed_data[key["member_id"]] = {}
            parsed_data[key["member_id"]][key["release_stream"]] = get_parsed_data(web_content)
            print("[got parsed data]")

        analyzed_data = get_analyzed_data(parsed_data)
        print("[got analyzed data]")

        releases = self.config_data["releases"]
        members = self.config_data["members"]
        pp_data = get_beautiful_data(analyzed_data, members, releases)
        print("[got beautiful data]", pp_data)

        notify(pp_data, members)
        print("[notification done]")

    @staticmethod
    def __help():
        help_msg = "web-notifier - usage\n" \
                   "\tmain.py [config_file]\n" \
                   "=============================\n" \
                   "config_file: a file that gives various setting to web-notifier\n" \
                   "             if not given, will search for \"%s\" at current directory" % DEFAULT_CONFIG_FILE
        print(help_msg)


if __name__ == '__main__':
    WebNotifier().run()

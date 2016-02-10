#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from htm_parse.parse import get_parsed_data
from pp.pretty_print import get_beautiful_data
from url_gen.generator import get_urls
from web_fetch.fetcher import get_web_content

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
        with open(config_file) as config_fp:
            self.config_data = json.load(config_fp)

    def run(self):
        print("web-notifier is running!")
        releases = self.config_data["releases"]
        members = self.config_data["members"]
        urls = get_urls(releases, members)
        for url in urls:
            print("[get url]", url)
            web_content = get_web_content(url)
            print("[get web content]", web_content)
            parsed_data = get_parsed_data(web_content)
            print("[get parsed data]", parsed_data)
            # here we can do post-analyze if required
            pp_data = get_beautiful_data(parsed_data)
            print("[get beautiful data]", pp_data)
            # after all, we call notifier to do notification

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

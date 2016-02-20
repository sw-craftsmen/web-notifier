#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import logging

from htm_parse.parse import get_parsed_data
from pp.pretty_print import get_beautiful_data
from url_gen.generator import UrlGenerator
from web_fetch.fetcher import get_web_content
from analyze.analyzer import get_analyzed_data
from notify.notifier import notify

DEFAULT_CONFIG_FILE = "config.json"

class WebNotifier(object):

    config_data = None
    args = None

    def __init__(self):

        arg_parser = ArgumentParser()
        arg_parser.add_argument("-c", "--config", 
            dest="config_file", default=DEFAULT_CONFIG_FILE, 
            help="config file name (default: '" + DEFAULT_CONFIG_FILE + "')")
        arg_parser.add_argument("-l", "--login",
            dest="web_login", default="", 
            help="web authentication login")
        arg_parser.add_argument("-p", "--password",
            dest="web_password", default="", 
            help="web authentication password")
        arg_parser.add_argument("-s", "--history_json",
            dest="history_json", default="", 
            help="history info in json format")
        arg_parser.add_argument("-x", "--excludes_json",
            dest="excludes_json", default="",
            help="exclude list in json format")
        arg_parser.add_argument("-v", "--verbose",
            dest="log_level", action="store_const", const=logging.INFO,
            help="show verbose info")

        self.args = arg_parser.parse_args()
        logging.basicConfig(level=self.args.log_level)

        self.__parse_config(self.args.config_file)

    def __parse_config(self, config_file):
        try:
            with open(config_file) as config_fp:
                import json
                self.config_data = json.load(config_fp)
        except IOError:
            print("Config file '" + config_file + "' does NOT exist!")
            exit()

    def run(self):
        logging.info("web-notifier is running!")

        parsed_data = {}

        for url, key in UrlGenerator(self.config_data):
            logging.info("[got url]" + url)

            web_content = get_web_content(url, self.args.web_login, self.args.web_password)
            logging.info("[got web content]")

            parsed_data[key["member_id"]] = {}
            parsed_data[key["member_id"]][key["release_stream"]] = get_parsed_data(web_content)
            logging.info("[got parsed data]")

        analyzed_data = get_analyzed_data(parsed_data)
        logging.info("[got analyzed data]")

        releases = self.config_data["releases"]
        members = self.config_data["members"]
        pp_data = get_beautiful_data(analyzed_data, members, releases)
        logging.info("[got beautiful data]" + pp_data)

        notify(pp_data, members)
        logging.info("[notification done]")

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

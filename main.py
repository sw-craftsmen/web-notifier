#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import collections
import logging
import os

from pp.pretty_print import get_beautiful_data, get_beautiful_pre_json
from util.content import get_content
from util.setting.post_analysis import file_modified_today

DEFAULT_CONFIG_FILE = "config.json"
DEFAULT_CONFIG_PRIVATE_FILE = "config_private.ini"
DEFAULT_OUTFILE = "output.json"


class WebNotifier(object):

    def __init__(self):
        arg_parser = ArgumentParser(description='Web Notifier --- notify exactly the web content you care about')
        arg_parser.add_argument("-c", "--config", dest="config_file", default=DEFAULT_CONFIG_FILE,
                                help="config file name (default: '%s')" % DEFAULT_CONFIG_FILE)
        arg_parser.add_argument("-cp", "--config_private",
                                dest="config_private_file", default=DEFAULT_CONFIG_PRIVATE_FILE,
                                help="config_private file name (default: '%s')" % DEFAULT_CONFIG_PRIVATE_FILE)
        arg_parser.add_argument("-o", "--output", dest="output", default=DEFAULT_OUTFILE,
                                help="output file name (default: '%s')" % DEFAULT_OUTFILE)
        arg_parser.add_argument("-l", "--login", dest="web_login", default="", help="web authentication login")
        arg_parser.add_argument("-p", "--password", dest="web_password", default="", help="web authentication password")
        arg_parser.add_argument("-v", "--verbose", dest="log_level", action="store_const",
                                const=logging.INFO, help="show verbose info")
        self.args = arg_parser.parse_args()
        logging.basicConfig(format='', level=self.args.log_level)

        from util.config import Config
        self.__config = Config(self.args.config_file)
        if os.path.exists(self.args.config_private_file):
            import configparser
            config_parser = configparser.ConfigParser()
            config_parser.read(self.args.config_private_file)
            if "" == self.args.web_login and config_parser.has_option("account", "username"):
                self.args.web_login = config_parser.get("account", "username")
            if "" == self.args.web_password and config_parser.has_option("account", "password"):
                self.args.web_password = config_parser.get("account", "password")

    def run(self):
        logging.info("[WbNt] web-notifier is running!")

        notify_data = collections.OrderedDict()  # key: notify_name, value: dict (see below)
        for notify_name in self.__config.notifications:
            print("[WbNt] dealing with notification \"%s\"" % notify_name)
            parsed_data = collections.OrderedDict()  # key: source key, value: list of parsed data
            notification = self.__config.notifications[notify_name]
            for entry in notification.get_key_and_path():
                assert isinstance(entry, list) and 2 == len(entry)
                [key, path] = entry
                key_str = "" if 0 == len(key) else \
                    str([key_value_pair[1] for key_value_pair in list(key.items())])
                print("[WbNt] %s" % key_str, end="")
                logging.info("[WbNt] " + path)
                content = get_content(path, self.args.web_login, self.args.web_password)
                WebNotifier.backup_content(key, content, notify_name)
                data_list = notification.parser.parse(content)
                if data_list:
                    assert type(data_list) is list
                    source_key = tuple(sorted(key.items()))  # convert to sorted-tuple, for dict is not hashable
                    parsed_data[source_key] = data_list
                    print("%sfind %i entry(s)" % (" => " if len(key_str) > 0 else "", len(data_list)), end="")
                print("")
            analyzed_data = notification.post_analysis.analyze(parsed_data, notify_data)
            notify_data[notify_name] = analyzed_data

        print(get_beautiful_data(notify_data))

        import json
        output_file = self.args.output
        with open(output_file, 'w') as write_fd:
            json.dump(get_beautiful_pre_json(notify_data), write_fd)

        logging.info("[WbNt] notification done")

    @staticmethod
    def backup_content(key, content, notify_name):
        assert isinstance(key, collections.OrderedDict)
        key_name = ""
        for entry in key:
            key_name += ("_" + key[entry])
        if "" == key_name:
            key_name = "_" + notify_name
        _, ext_name = os.path.splitext(content)
        backup_dir = "content_backup"
        if not os.path.exists(backup_dir):
            os.mkdir(backup_dir)
        content_name = key_name.replace(' ', '').replace('+', '_').replace('.', '') + ext_name
        immature_content_name = backup_dir + "/immature" + content_name
        mature_content_name = backup_dir + "/mature" + content_name
        from shutil import copyfile
        if not os.path.exists(mature_content_name) or not file_modified_today(mature_content_name):
            if os.path.exists(immature_content_name):
                copyfile(immature_content_name, mature_content_name)
        copyfile(content, immature_content_name)


if __name__ == '__main__':
    WebNotifier().run()

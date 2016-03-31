#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import logging
import os
import sys
from util.setting.notify import Notification


NOTIFY_KEY = "notification"


class Config(object):

    def __init__(self, config_file):
        if not os.path.exists(config_file):
            logging.warning("[config] config file \"%s\" does not exist, program exit..." % config_file)
            sys.exit()
        with open(config_file) as config_fp:
            import json
            config_data = json.load(config_fp, object_pairs_hook=collections.OrderedDict)

        self.notifications = collections.OrderedDict()  # key: notify_name, value: Notification
        notifications = config_data[NOTIFY_KEY] if NOTIFY_KEY in config_data else None
        if not notifications:
            logging.warning("[config] no notification specified, program exit...")
            sys.exit()
        for notify_name in notifications:
            self.notifications[notify_name] = Notification.create(notify_name, notifications[notify_name])

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    config_file = "../setting.json"
    config = Config(config_file)
    for name in config.notifications:
        print(name)
        key_and_path = config.notifications[name].get_key_and_path()
        for entry in key_and_path:
            assert isinstance(entry, list) and 2 == len(entry)
            [_, path] = entry
            print(path)

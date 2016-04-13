#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import logging
import os
import sys


NOTIFY_KEY = "notification"
AUDIENCE_KEY = "audience"


def adjust_path():  # TODO: remove duplication
    pre_path_list = []
    for path in sys.path:
        if "web-notifier" in path:
            pre_path_list.append(path)
    for path in pre_path_list:
        sys.path.insert(0, path)


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
            adjust_path()
            from util.setting.notify import Notification
            self.notifications[notify_name] = Notification.create(notify_name, notifications[notify_name])
        from util.setting.audience import Audience
        audiences = config_data[AUDIENCE_KEY] if AUDIENCE_KEY in config_data else None
        self.audiences = Audience.create(audiences)

if __name__ == '__main__':
    logging.basicConfig(format='', level=logging.DEBUG)
    #logging.basicConfig(format='')
    config_file = "sample.json"
    config = Config(config_file)
    config.audiences.notify("test_notify")

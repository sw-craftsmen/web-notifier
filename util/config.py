#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import logging
import os
import sys


NOTIFY_KEY = "notification"
AUDIENCE_KEY = "audience"


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
            from wbnt_path import adjust_path
            adjust_path()
            from util.setting.notify import Notification
            self.notifications[notify_name] = Notification.create(notify_name, notifications[notify_name])
        from util.setting.audience import Audience
        audiences = config_data[AUDIENCE_KEY] if AUDIENCE_KEY in config_data else None
        self.audiences = Audience.create(audiences)

if __name__ == '__main__':
    logging.basicConfig(format='', level=logging.DEBUG)
    # logging.basicConfig(format='')
    config_file = "sample.json"
    config = Config(config_file)
    config.audiences.notify("test_notification_message")

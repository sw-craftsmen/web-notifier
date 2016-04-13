#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import os
import sys
import unittest


def get_file(filename):
    ret_file = filename
    if not os.path.exists(ret_file):
        os.chdir("util/setting/unittest")
    assert os.path.exists(ret_file)
    return ret_file


def adjust_path():
    pre_path_list = []
    for path in sys.path:
        if "web-notifier" in path:
            pre_path_list.append(path)
    for path in pre_path_list:
        sys.path.insert(0, path)


class PostAnalysisTest(unittest.TestCase):
    __config_data = None

    def setUp(self):
        adjust_path()

    def perform_test(self, name, setting_file, golden_file):
        print("%s test" % name, end="")
        sys.stdout.flush()
        from util.config import Config
        config = Config(get_file(setting_file))

        notify_data = collections.OrderedDict()
        for notify_name in config.notifications:
            parsed_data = collections.OrderedDict()
            notification = config.notifications[notify_name]
            for entry in notification.get_key_and_path():
                [key, path] = entry
                from util.content import get_content
                content = get_content(path)
                data_list = notification.parser.parse(content)
                assert data_list and type(data_list) is list
                source_key = tuple(sorted(key.items()))  # convert to sorted-tuple, for dict is not hashable
                parsed_data[source_key] = data_list
            analyzed_data = notification.post_analysis.analyze(parsed_data, notify_data)
            notify_data[notify_name] = analyzed_data
            os.remove("immature_" + notify_name + ".txt")
            os.remove("mature_" + notify_name + ".txt")
        with open(get_file(golden_file), encoding='utf8') as f:
            golden = f.read()
        from pp.pretty_print import get_beautiful_data
        self.assertEqual(get_beautiful_data(notify_data), golden)

    def test_remap(self):
        self.perform_test("remap", "setting_remap.json", "golden_remap.txt")

    def test_exclude(self):
        self.perform_test("exclude", "setting_exclude.json", "golden_exclude.txt")

    def test_exclude_uncond(self):
        self.perform_test("exclude_uncond", "setting_exclude_uncond.json", "golden_exclude_uncond.txt")

    def test_avoid_duplicate(self):
        self.perform_test("avoid_duplicate", "setting_avoid_duplicate.json", "golden_avoid_duplicate.txt")


if __name__ == '__main__':
    unittest.main()

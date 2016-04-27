#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest


def get_file(filename):
    ret_file = filename
    if not os.path.exists(ret_file):
        os.chdir("util/setting/unittest")
    assert os.path.exists(ret_file)
    return ret_file


class SourceTest(unittest.TestCase):
    __config_data = None

    def setUp(self):
        from wbnt_path import adjust_path
        adjust_path()

    def test_source(self):
        print("source test", end="")
        sys.stdout.flush()
        from util.config import Config
        config = Config(get_file("setting_source.json"))

        cycle_entries = []
        for notify_name in config.notifications:
            notification = config.notifications[notify_name]
            for entry in notification.get_key_and_path():
                cycle_entries.append(str(entry))

        golden_file = get_file("golden_source.txt")
        with open(golden_file, encoding='utf8') as f:
            golden_entries = f.read().splitlines()

        self.assertEqual(len(cycle_entries), len(golden_entries))
        for cycle, golden in zip(cycle_entries, golden_entries):
            self.assertEqual(cycle, golden)


if __name__ == '__main__':
    unittest.main()

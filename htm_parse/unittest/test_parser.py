#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest


def get_file(filename):
    ret_file = filename
    if not os.path.exists(ret_file):
        ret_file = "htm_parse/unittest/" + ret_file
    assert os.path.exists(ret_file)
    return ret_file


class HtmParserTest(unittest.TestCase):
    __config_data = None

    def setUp(self):
        from wbnt_path import adjust_path
        adjust_path()

    def test_htm_parse(self):
        print("htm parser test", end="")
        sys.stdout.flush()
        htm_file = get_file("weather.htm")
        from htm_parse.parser import HtmTableDataRetriever, IsValidSegment
        is_match_pattern = IsValidSegment(["Hanoi", "Melbourne", "Singapore"], exact_match=True)
        target_sequence = ["City", "Weather", "Temperature(℃)"]
        from util.setting.parser import HtmParseSetting, REMOVE_WS_KEY, TRUE, STRIP_KEY
        setting = HtmParseSetting({REMOVE_WS_KEY: TRUE, STRIP_KEY: TRUE})
        retriever = HtmTableDataRetriever(htm_file, is_match_pattern, target_sequence, setting)

        golden_file = get_file("golden.txt")
        with open(golden_file, encoding='utf8') as f:
            golden_entries = f.read().splitlines()

        self.assertEqual(len(retriever), len(golden_entries))
        for cycle, golden in zip(retriever, golden_entries):
            import collections
            sorted_cycle = collections.OrderedDict(sorted(cycle.items()))
            self.assertEqual(str(sorted_cycle), golden)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest


class HtmParserTest(unittest.TestCase):
    __config_data = None

    def setUp(self):
        print("===============")
        print("htm parser test")
        print("===============")

    def test_htm_parse(self):
        htm_file = "weather.htm"
        from parser import HtmDataRetriever, IsValidSegment
        is_match_pattern = IsValidSegment(["Hanoi", "Melbourne", "Singapore"], exact_match=True)
        target_sequence = ["City", "Weather", "Temperature(℃)"]
        retriever = HtmDataRetriever(htm_file, is_match_pattern, target_sequence)

        golden_file = "golden.txt"
        with open(golden_file) as f:
            golden_entries = f.read().splitlines()

        self.assertEqual(len(retriever), len(golden_entries))
        for cycle, golden in zip(retriever, golden_entries):
            import collections
            sorted_cycle = collections.OrderedDict(sorted(cycle.items()))
            self.assertEqual(str(sorted_cycle), golden)


if __name__ == '__main__':
    unittest.main()

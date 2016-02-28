#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import unittest
from generator import UrlGenerator


class UrlGeneratorTest(unittest.TestCase):
    __config_data = None

    def setUp(self):
        print("==================")
        print("Url generator test")
        print("==================")
        config_file = "../config.json"
        with open(config_file) as config_fp:
            self.__class__.__config_data = json.load(config_fp)

    def test_url(self):
        golden_file = "golden.txt"
        with open(golden_file) as f:
            golden_urls = f.read().splitlines()
        cycle_url_count = 0
        for url_cycle, unused_key in UrlGenerator(self.__class__.__config_data):
            self.assertIn(url_cycle, golden_urls)
            cycle_url_count += 1
        self.assertEqual(cycle_url_count, len(golden_urls))

if __name__ == '__main__':
    unittest.main()

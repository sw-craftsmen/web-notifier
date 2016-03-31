#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from htm_parse.parser import get_parsed_data


KEY_KEY = "key"
COLUMNS_KEY = "columns"


class HtmParser(object):
    def __init__(self, data):
        assert isinstance(data, dict) and KEY_KEY in data and COLUMNS_KEY in data
        self.key = data[KEY_KEY]
        columns = data[COLUMNS_KEY]
        assert isinstance(columns, list)
        self.columns = columns

    def parse(self, content):
        return get_parsed_data(content, self.key, self.columns)


class TxtParser(object):
    def __init__(self, data):
        assert isinstance(data, dict) and KEY_KEY in data
        self.key = data[KEY_KEY]

    # currently, use 'key' as 'containing' checking, if check success, get value of string before a blank char
    def parse(self, content):
        with open(content, 'r') as fd:
            found_values = []
            for line_str in fd.readlines():
                if self.key in line_str:
                    end_pos = line_str.find(" ")
                    assert -1 != end_pos
                    value = line_str[:end_pos]
                    found_values.append(value)
            return found_values


class Parser(object):
    def __init__(self):
        pass

    @staticmethod
    def create(data):
        assert isinstance(data, dict) and 1 == len(data)
        rule_type = None
        for key in data:
            rule_type = key
        if "htm" == rule_type:
            return HtmParser(data[rule_type])
        elif "txt" == rule_type:
            return TxtParser(data[rule_type])
        else:
            assert False, rule_type

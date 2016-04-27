#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from htm_parse.parser import get_parsed_data
import collections

KEY_KEY = "key"
COLUMNS_KEY = "columns"
SEPERATOR_KEY = "seperator"
GLOBAL_KEY = "global_keys"


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
        assert isinstance(data, dict) and KEY_KEY in data and COLUMNS_KEY in data and SEPERATOR_KEY in data
        self.key = data[KEY_KEY]
        columns = data[COLUMNS_KEY]
        assert isinstance(columns, list)
        self.columns = columns
        self.seperator = data[SEPERATOR_KEY]
        self.global_keys = data[GLOBAL_KEY] if GLOBAL_KEY in data else {}

    # currently, use 'key' as 'containing' checking, if check success, get value of string before a blank char
    def parse(self, content):
        with open(content, 'r') as fd:
            found_values = []
            global_keys = collections.OrderedDict()
            for line_str in fd.readlines():
                if self.key in line_str:
                    entry = line_str.split(self.seperator)
                    found_value = collections.OrderedDict()
                    for i in range(len(entry)):
                        found_value[self.columns[i]] = entry[i]
                    found_values.append(found_value)
                for key, value in self.global_keys.items():
                    if value in line_str:
                        end_pos = line_str.find(" ")
                        assert -1 != end_pos
                        global_keys[key] = line_str[end_pos:]
            # fill global_keys to all found_values
            for key, value in global_keys.items():
                for found_value in found_values:
                    found_value[key] = value
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

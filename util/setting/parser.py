#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os

TRUE = "True"
FALSE = "False"


def get_bool_value(value):
    if type(value) is str:
        assert value in [TRUE, FALSE]
        return value == TRUE
    assert not value or type(value) is bool
    return value


def get_value_from_str(data, key, default, is_bool):
    if key in data:
        raw_data = data[key]
        return get_bool_value(raw_data) if is_bool else raw_data
    else:
        return default


STRIP_KEY = "strip"
COMBINE_BR_KEY = "combine_br"
REMOVE_WS_KEY = "remove_ws"
REMOVE_HYPERLINK_KEY = "remove_hyperlink"
REMOVE_LIST_KEY = "remove_list"
STOP_KEY = "stop"

DEFAULT_STRIP = False  # to make ' yyy ' as 'yyy'
DEFAULT_COMBINE_BR = True  # to make 'a<br>b' as 'ab'
DEFAULT_REMOVE_WS = False  # to make 'a b' as 'ab'
DEFAULT_REMOVE_HYPERLINK = True  # to make '<a href=...>xxx</a>' as 'xxx'


class HtmParseSetting(object):
    def __init__(self, data):
        self.strip = get_value_from_str(data, STRIP_KEY, DEFAULT_STRIP, True)
        self.combine_br = get_value_from_str(data, COMBINE_BR_KEY, DEFAULT_COMBINE_BR, True)
        self.remove_ws = get_value_from_str(data, REMOVE_WS_KEY, DEFAULT_REMOVE_WS, True)
        self.remove_hyperlink = get_value_from_str(data, REMOVE_HYPERLINK_KEY, DEFAULT_REMOVE_HYPERLINK, True)
        self.remove_list = get_value_from_str(data, REMOVE_LIST_KEY, None, False)
        self.stop = get_value_from_str(data, STOP_KEY, None, False)


KEY_KEY = "key"


class HtmParserBase(object):
    def __init__(self, data):
        assert isinstance(data, dict) and KEY_KEY in data
        raw_data = data[KEY_KEY]
        assert type(raw_data) in [str, list]
        self.patterns = [re.compile(raw_data)] if type(raw_data) is str else [re.compile(item) for item in raw_data]
        self.setting = HtmParseSetting(data)

    # play as the role of 'is_match_pattern'
    def __call__(self, test_pattern):
        for pattern in self.patterns:
            if None is not re.match(pattern, test_pattern):
                return True
        return False


def is_content_okay(content):
    return content and os.path.exists(content)


def get_retrieved_data(retriever, expected_data_len):
    data = []
    for retrieved_data in retriever:
        import copy
        data.append(copy.deepcopy(retrieved_data))
        assert len(retrieved_data) == expected_data_len
    return data


COLUMNS_KEY = "columns"


class HtmTableParser(HtmParserBase):
    def __init__(self, data):
        super(HtmTableParser, self).__init__(data)
        assert COLUMNS_KEY in data
        columns = data[COLUMNS_KEY]
        assert isinstance(columns, list)
        self.columns = columns

    def parse(self, content):
        if not is_content_okay(content):
            return None

        from htm_parse.parser import HtmTableDataRetriever
        retriever = HtmTableDataRetriever(content, self, self.columns, self.setting)
        return get_retrieved_data(retriever, len(self.columns))


ENTRIES_KEY = "entries"


class HtmParser(HtmParserBase):
    def __init__(self, data):
        super(HtmParser, self).__init__(data)
        assert ENTRIES_KEY in data
        entries = data[ENTRIES_KEY]
        assert isinstance(entries, list)
        self.entries = entries

    def parse(self, content):
        if not is_content_okay(content):
            return None

        from htm_parse.parser import HtmDataRetriever
        retriever = HtmDataRetriever(content, self, self.entries, self.setting)
        return get_retrieved_data(retriever, len(self.entries))


class TxtParser(object):
    def __init__(self, data):
        assert isinstance(data, dict) and KEY_KEY in data
        self.key = data[KEY_KEY]

    # currently, use 'key' as 'containing' checking, if check success, get value of string before a blank char
    def parse(self, content):
        with open(content, 'r', errors='ignore') as fd:  # ignore error in general may hide some decoding issue...
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
        if "htm_table" == rule_type:
            return HtmTableParser(data[rule_type])
        if "htm" == rule_type:
            return HtmParser(data[rule_type])
        if "txt" == rule_type:
            return TxtParser(data[rule_type])
        assert False, rule_type

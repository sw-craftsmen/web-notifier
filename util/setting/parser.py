#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from htm_parse.parser import get_parsed_data
import collections
import re
import os


class Parser(object):
    def __init__(self):
        self.informative = {}  # entries with 'informative' attribute => to let such entry change not result in 'new'

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


class HtmParserBase(Parser):
    def __init__(self, data):
        super(HtmParserBase, self).__init__()
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
SEPERATOR_KEY = "seperator"
GLOBAL_KEY = "global_keys"


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
INFORMATIVE_KEY = "informative"


class HtmParser(HtmParserBase):
    def __init__(self, data):
        super(HtmParser, self).__init__(data)
        assert ENTRIES_KEY in data
        entries = data[ENTRIES_KEY]
        assert isinstance(entries, list)
        self.entries = entries
        for entry in self.entries:
            if len(entry) > 2 and INFORMATIVE_KEY in entry[2:]:
                name = entry[1]
                self.informative[name] = True  # 'True' is a dummy value

    def parse(self, content):
        if not is_content_okay(content):
            return None

        from htm_parse.parser import HtmDataRetriever
        retriever = HtmDataRetriever(content, self, self.entries, self.setting)
        return get_retrieved_data(retriever, len(self.entries))


class TxtParser(Parser):
    def __init__(self, data):
        super(TxtParser, self).__init__()
        assert isinstance(data, dict) and KEY_KEY in data and COLUMNS_KEY in data and SEPERATOR_KEY in data
        self.key = data[KEY_KEY]
        columns = data[COLUMNS_KEY]
        assert isinstance(columns, list)
        self.columns = columns
        self.seperator = data[SEPERATOR_KEY]
        self.global_keys = data[GLOBAL_KEY] if GLOBAL_KEY in data else {}

    # currently, use 'key' as 'containing' checking, if check success, get value of string before a blank char
    def parse(self, content):
        with open(content, 'r', errors='ignore') as fd:  # ignore error in general may hide some decoding issue...
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

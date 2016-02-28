#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import html.parser
import logging
import os


class PosSpec(object):

    def __init__(self, is_start_value=None, max_trial_cnt=None):
        self.__is_start_value = is_start_value
        self.__max_trial_cnt = max_trial_cnt
        self.spec = []

    def add_spec(self, name, is_target_value, might_fail=False):
        self.spec.append([name, is_target_value, might_fail])

    def is_start_value(self, data):
        if not self.__is_start_value:
            return True
        return self.__is_start_value(data)

    def max_trial_cnt(self):
        return self.__max_trial_cnt

    def is_all_target_found(self, retrieved_name):
        for spec_iter in self.spec:
            [name, _, might_fail] = spec_iter
            if not might_fail and name not in retrieved_name:
                return False
        return True


class HTMSpec(object):
    """define what the type of value and how the value will be retrieved"""

    def __init__(self):
        self.spec = []
        self.__spec_positions = {}
        self.__spec_value_tuples = {}  # key: spec name, value: value_tuple_list

    # spec provide a two-level checking: 1. is_valid, 2. is_match
    def add_spec(self, name, is_valid, value_tuple_list, is_match=None, skip_cnt_after_match=None):
        self.spec.append([name, is_valid, is_match, skip_cnt_after_match])
        self.__spec_value_tuples[name] = value_tuple_list
        positions = []
        for value_tuple in value_tuple_list:
            [_, position, _] = value_tuple
            positions.append(position)
        self.__spec_positions[name] = positions

    def get_required_position(self, spec_name):
        return self.__spec_positions[spec_name]

    def get_value_tuple(self, spec_name, position):
        for value_tuple in self.__spec_value_tuples[spec_name]:
            [_, value_position, _] = value_tuple
            if value_position == position:
                return value_tuple
        assert False


class HtmAnalyzer(object):

    def __init__(self, htm_file):
        assert type(htm_file) is str
        self.__htm_file = htm_file
        self.__content = None
        self.__value_map = {}
        self.cur_spec_name = None
        self.__cur_match = False

    def access(self):
        if not os.path.exists(self.__htm_file):
            logging.warning("htm file \'%s\' does not exist" % self.__htm_file)
            return False
        # with open(self.__htm_file, encoding='latin-1') as fd:
        with open(self.__htm_file) as fd:
            web_content = fd.read()
        self.__content = iter(HTMLParser().parse_and_retrieve(web_content))
        return True

    def read_pos(self, spec):
        iter_pos = 1
        start_retrieval_pos = 0
        retrieved_name = []
        in_retrieval = False
        for data in self.__content:
            if not in_retrieval:
                in_retrieval = spec.is_start_value(data)
                continue
            if in_retrieval:
                if spec.max_trial_cnt():
                    progress_cnt = iter_pos - start_retrieval_pos
                    if progress_cnt > spec.max_trial_cnt():
                        return False
                for spec_iter in spec.spec:
                    [name, is_target_value, _] = spec_iter
                    if name in retrieved_name:
                        continue
                    if is_target_value(data):
                        self.__value_map[name] = progress_cnt
                        retrieved_name.append(name)
                    if spec.is_all_target_found(retrieved_name):
                        return True
            iter_pos += 1
        return False

    # use to skip certain amount of data from current htm content
    def skip_data(self, skip_cnt):
        if not skip_cnt:
            return
        for _ in self.__content:
            skip_cnt -= 1
            if skip_cnt <= 0:
                return

    def read(self, spec):
        acquired = False
        iter_pos = 0
        start_retrieval_pos = 0
        retrieved_pos = []
        in_retrieval = False
        for data in self.__content:
            if not in_retrieval:
                valid_spec_name, is_match, skip_cnt_after_match = get_valid_spec_name(data, spec)
                if not valid_spec_name:
                    continue
                # need reset it (or use deepcopy), for 'dict' may be mutated
                in_retrieval = True
                self.cur_spec_name, self.__cur_match = valid_spec_name, is_match
                start_retrieval_pos = iter_pos
            if in_retrieval:
                progress_cnt = iter_pos - start_retrieval_pos
                if progress_cnt in spec.get_required_position(self.cur_spec_name):
                    [value_name, _, value_type] = spec.get_value_tuple(self.cur_spec_name, progress_cnt)
                    spec_value = get_spec_value(data, value_type)
                    if self.__cur_match:
                        self.__value_map[value_name] = spec_value
                    retrieved_pos.append(progress_cnt)
                    if retrieved_pos == spec.get_required_position(self.cur_spec_name):
                        self.skip_data(skip_cnt_after_match)
                        if self.__cur_match:
                            return True
                        retrieved_pos = []
                        in_retrieval = False
                        continue
            iter_pos += 1
        return acquired

    def get_value(self, key, might_fail=False):
        if key not in self.__value_map:
            assert might_fail, "key: \"" + key + "\" does not exist in op_htm handler"
            return None
        return self.__value_map[key]

    def get_values(self, keys):
        values = []
        for key in keys:
            values.append(self.get_value(key))
        return values


def get_valid_spec_name(data, spec):
    """traverse all spec and return the result: found_spec_name, is_data_match, skip_cnt_post_match"""
    for spec_iter in spec.spec:
        [spec_name, is_valid, is_match, skip_cnt_post_match] = spec_iter
        if not is_valid(data):
            continue
        return spec_name, not is_match or is_match(data), skip_cnt_post_match
    return None, False, None


def get_spec_value(data, value_type):
    data = data.replace(',', '')
    try:
        value = value_type(data)
    except ValueError as msg:
        print(data, value_type)
        assert False, msg
    return value


# Note: this routine has poor performance (as it can call so many times)
def decorate(segments, need_encode=True, remove_comma=True, remove_ws=True):
    ret = []
    for seg in segments:
        if remove_ws:
            seg = seg.replace(' ', '')
        if remove_comma:
            seg = seg.replace(',', '')
        if need_encode:
            seg = seg.decode('cp950').encode('utf-8')
        ret.append(seg)
    return ret


class HTMLParser(html.parser.HTMLParser):
    """handle the htm source data: parse it to token list"""

    __in_br = False

    def parse_and_retrieve(self, htm_content, combine_br=True, ws_delim=False):
        """parse and keep the processed token"""
        self.__tokens = []
        self.__combine_br = combine_br
        self.feed(htm_content.replace("&nbsp;", " ").replace("></A>", "> </A>"))
        self.__tokens = decorate(self.__tokens, need_encode=False, remove_comma=False, remove_ws=not ws_delim)
        if ws_delim:
            delim_list = []
            for token in self.__tokens:
                non_ws_list = token.split()  # will split on all whitespace
                for non_ws_seg in non_ws_list:
                    delim_list.append(non_ws_seg)
            return delim_list
        return self.__tokens

    def handle_data(self, data):
        """HTMLParser.feed() invokes this routine when met data within tag"""
        if not HTMLParser.__in_br or not self.__combine_br:
            self.__tokens.append(u'%s' % data)
        if HTMLParser.__in_br:
            HTMLParser.__in_br = False
            # 'a<br>b' => 'ab' (to support correct PosSpec reading)
            if self.__combine_br:
                self.__tokens[len(self.__tokens) - 1] += (u'%s' % data)

    def handle_starttag(self, tag, attrs):
        if "br" == tag:
            HTMLParser.__in_br = True

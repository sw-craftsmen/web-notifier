#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import html.parser
import logging
import re
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

    def __init__(self, htm_file, setting):
        assert type(htm_file) is str
        self.__htm_file = htm_file
        self.__content = []
        self.__value_map = {}
        self.cur_spec_name = None
        self.__cur_match = False
        self.setting = setting

    def access(self):
        if not os.path.exists(self.__htm_file):
            logging.warning("htm file \'%s\' does not exist" % self.__htm_file)
            return False
        # with open(self.__htm_file, encoding='latin-1') as fd:
        with open(self.__htm_file, encoding='utf8') as fd:
            web_content = fd.read()
        # we don't care font setting in html
        web_content = re.sub('<font.*?>', '', web_content.replace('</font>', ''))
        if self.setting.remove_hyperlink:
            web_content = HtmAnalyzer.remove_hyperlink_tag(web_content)
        self.__content = iter(HTMLParser().parse_and_retrieve(web_content, setting=self.setting))
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

    @staticmethod
    def remove_hyperlink_tag(content):
        return re.sub('<a href.*?>', '', content.replace('</a>', ''))


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
def decorate(segments, remove_list, strip=False, need_encode=True, remove_comma=True, remove_ws=True):
    ret = []
    for seg in segments:
        if strip:
            seg = seg.strip()
        if remove_ws:
            seg = seg.replace(' ', '')
        if remove_comma:
            seg = seg.replace(',', '')
        if need_encode:
            seg = seg.decode('cp950').encode('utf-8')
        if remove_list:
            for remove_item in remove_list:
                if remove_item in seg:
                    seg = ''
        ret.append(seg)
    return ret


class HTMLParser(html.parser.HTMLParser):
    """handle the htm source data: parse it to token list"""

    __in_br = False
    __met_stop = False

    @staticmethod
    def replace_content(content, replace_pair_list):
        for [rep_from, rep_to] in replace_pair_list:
            content = content.replace(rep_from, rep_to)
        assert '→' not in content
        return content

    def parse_and_retrieve(self, htm_content, setting, ws_delim=False):
        """parse and keep the processed token"""
        self.__tokens = []
        self.__combine_br = setting.combine_br
        self.__stop = setting.stop
        replace_pair_list = [['\n', ''], ['\t', ''], ["&nbsp;", " "], ["></A>", "> </A>"]]
        self.feed(HTMLParser.replace_content(htm_content, replace_pair_list))
        self.__tokens = decorate(self.__tokens,
                                 remove_list=setting.remove_list, strip=setting.strip, remove_ws=setting.remove_ws,
                                 need_encode=False, remove_comma=False)
        if setting.strip:
            self.__tokens = list(filter(len, self.__tokens))
            for item in self.__tokens:
                assert len(item) > 0
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
        if HTMLParser.__met_stop:
            return
        if self.__stop and self.__stop in data:
            HTMLParser.__met_stop = True
            return
        if not HTMLParser.__in_br or not self.__combine_br:
            self.__tokens.append(u'%s' % data)
        if HTMLParser.__in_br:
            HTMLParser.__in_br = False
            # 'a<br>b' => 'ab' (to support correct PosSpec reading)
            if self.__combine_br:
                self.__tokens[len(self.__tokens) - 1] += (u'%s' % data)

    def handle_starttag(self, tag, attrs):
        HTMLParser.__in_br = "br" == tag


if __name__ == '__main__':
    from argparse import ArgumentParser
    arg_parser = ArgumentParser(description="Test utility for HTMLParser")
    arg_parser.add_argument('htm_file')
    arg_parser.add_argument("-s", "--strip", dest="strip", action="store_const",
                            const=True, help="strip (default: '%s')" % False)
    arg_parser.add_argument("-c", "--combine_br", dest="combine_br", action="store_const",
                            const=True, help="combine <br> (default: '%s')" % False)
    arg_parser.add_argument("-rmw", "--remove_ws", dest="remove_ws", action="store_const",
                            const=True, help="remove whitespace (default: '%s')" % False)
    arg_parser.add_argument("-rmh", "--remove_hyperlink", dest="remove_hyperlink", action="store_const",
                            const=True, help="remove hyperlink tag (default: '%s')" % False)
    args = arg_parser.parse_args()
    if not args.htm_file or not os.path.exists(args.htm_file):
        import sys
        sys.exit()
    with open(args.htm_file, encoding='utf8') as fd:
        web_content = fd.read()
    if args.remove_hyperlink:
        web_content = HtmAnalyzer.remove_hyperlink_tag(web_content)
    from wbnt_path import adjust_path
    adjust_path()
    from util.setting.parser import HtmParseSetting, STRIP_KEY, REMOVE_WS_KEY, REMOVE_LIST_KEY, COMBINE_BR_KEY
    remove_list = None
    setting = HtmParseSetting({STRIP_KEY: args.strip, REMOVE_WS_KEY: args.remove_ws,
                               REMOVE_LIST_KEY: remove_list, COMBINE_BR_KEY: args.combine_br})
    content = HTMLParser().parse_and_retrieve(web_content, setting=setting)
    for i, line in zip(range(len(content)), content):
        print(i, "=>", line)

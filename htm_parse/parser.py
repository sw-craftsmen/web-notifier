#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os


def get_parsed_data(web_page, key, sequence):
    if not web_page or not os.path.exists(web_page):
        return None

    import re
    re_pattern = re.compile(key)

    def is_match_pattern(test_pattern):
        return None is not re.match(re_pattern, test_pattern)

    cases = []
    for retrieved_data in HtmDataRetriever(web_page, is_match_pattern, sequence):
        import copy
        cases.append(copy.deepcopy(retrieved_data))
        assert len(retrieved_data) == len(sequence)
        """for pattern in sequence:
             print("%s => %s" % (pattern, retrieved_data[pattern]))"""
    return cases


class IsValidSegment(object):
    def __init__(self, spec, exact_match=True):
        self.__spec = spec
        self.__exact_match = exact_match

    def __call__(self, segment):
        if not self.__spec:
            return False
        if self.__exact_match:
            return segment in self.__spec
        else:
            for spec_iter in self.__spec:
                if spec_iter in segment:
                    return True
            return False


class HtmDataRetriever(object):

    def __init__(self, htm_file, is_match_pattern, target_sequence, data_spread_length=30):
        assert is_match_pattern and type(target_sequence) is list and type(data_spread_length) is int
        self.__values, self.__size = HtmDataRetriever.retrieve(htm_file, is_match_pattern, target_sequence,
                                                               data_spread_length)

    def __iter__(self):
        return self

    def __next__(self):
        return self.__values.__next__()

    def __len__(self):
        return self.__size

    @staticmethod
    def retrieve(htm_file, is_match_pattern, target_sequence, data_spread_length):
        assert type(htm_file) is str
        empty_iter = iter([]), 0
        if not os.path.exists(htm_file):
            logging.warning("[parser] htm file \'%s\' does not exist" % htm_file)
            return empty_iter
        if not target_sequence:
            logging.warning("[parser] no target sequence specified")
            return empty_iter

        from htm_parse.parse_engine import HtmAnalyzer, HTMSpec, PosSpec
        analyzer = HtmAnalyzer(htm_file)
        if not analyzer.access():
            logging.warning("[parser] htm analyzer failed!")
            return empty_iter

        start_pattern = target_sequence[0]
        subsequent_patterns = target_sequence[1:]
        pos_spec = PosSpec(IsValidSegment([start_pattern]), data_spread_length)
        for pattern in subsequent_patterns:
            pos_spec.add_spec(pattern, IsValidSegment([pattern]))
        if not analyzer.read_pos(pos_spec):
            logging.debug("[parser] cannot find matched sequence")
            return empty_iter

        logging.debug("[parser] find sequence no: " + "%i " * (len(subsequent_patterns)) %
                      tuple(analyzer.get_values(subsequent_patterns)))
        value_spec = [[start_pattern, 0, str]]  # start_pattern has position '0;
        for pattern in subsequent_patterns:
            value_spec.append([pattern, analyzer.get_value(pattern), str])
        htm_spec = HTMSpec()
        htm_spec.add_spec("spec_name", is_match_pattern, value_spec)  # we only support one spec. for HtmDataRetriever
        values_list = []
        while analyzer.read(htm_spec):
            import collections
            value_dict = collections.OrderedDict()
            for pattern in target_sequence:
                value_dict[pattern] = analyzer.get_value(pattern)
            values_list.append(value_dict)
        return iter(values_list), len(values_list)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    htm_file = "weather.htm"
    is_match_pattern = IsValidSegment(["Hanoi", "Melbourne", "Singapore"], exact_match=True)
    target_sequence = ["City", "Weather", "Temperature(℃)"]
    for retrieved_data in HtmDataRetriever(htm_file, is_match_pattern, target_sequence):
        for pattern in target_sequence:
            print("%s => %s" % (pattern, retrieved_data[pattern]))

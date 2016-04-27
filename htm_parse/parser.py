#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os


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


class HtmDataRetrieverBase(object):
    def __init__(self, htm_file, setting):
        assert type(htm_file) is str
        self._htm_file = htm_file
        self._setting = setting
        self._values = []
        self._size = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self._values.__next__()

    def __len__(self):
        return self._size

    def _get_analyzer(self):
        if not os.path.exists(self._htm_file):
            logging.warning("[parser] htm file \'%s\' does not exist" % self._htm_file)
            return None
        from htm_parse.parse_engine import HtmAnalyzer
        analyzer = HtmAnalyzer(self._htm_file, self._setting)
        if not analyzer.access():
            logging.warning("[parser] htm analyzer failed!")
            return None
        return analyzer

    @staticmethod
    def _get_value_iters(analyzer, spec, name_list):
        values_list = []
        while analyzer.read(spec):
            import collections
            value_dict = collections.OrderedDict()
            for name in name_list:
                value_dict[name] = analyzer.get_value(name)
            values_list.append(value_dict)
        return iter(values_list), len(values_list)


class HtmTableDataRetriever(HtmDataRetrieverBase):
    def __init__(self, htm_file, is_match_pattern, target_sequence, setting, data_spread_length=30):
        super(HtmTableDataRetriever, self).__init__(htm_file, setting)
        assert is_match_pattern and type(target_sequence) is list and type(data_spread_length) is int
        self._values, self._size = self.retrieve(is_match_pattern, target_sequence, data_spread_length)

    def retrieve(self, is_match_pattern, target_sequence, data_spread_length):
        empty_iter = iter([]), 0
        if not target_sequence:
            logging.warning("[parser] no target sequence specified")
            return empty_iter
        analyzer = self._get_analyzer()
        if not analyzer:
            return empty_iter

        from htm_parse.parse_engine import HTMSpec, PosSpec
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
        htm_spec.add_spec("spec_name", is_match_pattern, value_spec)  # we only support one spec. now
        return HtmDataRetrieverBase._get_value_iters(analyzer, htm_spec, target_sequence)


class HtmDataRetriever(HtmDataRetrieverBase):
    def __init__(self, htm_file, is_match_pattern, entries, setting):
        super(HtmDataRetriever, self).__init__(htm_file, setting)
        assert type(entries) is list
        self._values, self._size = self.retrieve(is_match_pattern, entries)

    def retrieve(self, is_match_pattern, entries):
        empty_iter = iter([]), 0
        if not entries:
            logging.warning("[parser] no target entry specified")
            return empty_iter
        analyzer = self._get_analyzer()
        if not analyzer:
            return empty_iter

        value_spec = []
        for entry in entries:
            pos, name = entry[0], entry[1]
            value_spec.append([name, pos, str])
        from htm_parse.parse_engine import HTMSpec
        htm_spec = HTMSpec()
        htm_spec.add_spec("spec_name", is_match_pattern, value_spec)  # we only support one spec. now
        return HtmDataRetrieverBase._get_value_iters(analyzer, htm_spec, [entry[1] for entry in entries])


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    pass

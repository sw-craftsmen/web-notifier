#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
from util.setting.source import Source
from util.setting.parser import Parser
from util.setting.post_analysis import PostAnalysis

SOURCE_KEY = "source"
PARSE_RULE_KEY = "parse_rule"
POST_ANALYSIS_KEY = "post_analysis"


class Notification(object):
    def __init__(self, source=None, parse_rule=None, post_analysis=None, pretty_print=None):
        self.source = source
        self.parser = parse_rule
        self.post_analysis = post_analysis
        self.pretty_print = pretty_print

    @staticmethod
    def create(name, data):
        assert isinstance(data, dict)

        logging.debug("[notify] notification: %s" % name)
        raw_source = data[SOURCE_KEY] if SOURCE_KEY in data else None
        raw_parse_rule = data[PARSE_RULE_KEY] if PARSE_RULE_KEY in data else None
        raw_post_analysis = data[POST_ANALYSIS_KEY] if POST_ANALYSIS_KEY in data else None
        if not raw_source:
            logging.warning("[notify] no source specified in \"%s\", program exit..." % name)
        if not raw_parse_rule:
            logging.warning("[notify] no parse rule specified in \"%s\", program exit..." % name)
        return Notification(Source.create(raw_source),
                            Parser.create(raw_parse_rule),
                            PostAnalysis.create(name, raw_post_analysis))

    def get_key_and_path(self):
        key_and_path = []
        for entry in self.source:
            key_and_path.append(entry)
        return key_and_path

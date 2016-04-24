#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import logging
import os

EXCLUDE_KEY = "exclude"
REMAP_KEY = "re-map"
AVOID_DUP_KEY = "avoid_duplicate"


def file_modified_today(filename):
    assert os.path.exists(filename)
    import datetime
    str_mdate = datetime.datetime.fromtimestamp(os.path.getmtime(filename)).strftime("%Y%m%d")
    str_today = datetime.datetime.today().strftime("%Y%m%d")
    return str_mdate == str_today


class PostAnalysis(object):
    def __init__(self, name, exclude_setting=None, remap_setting="", avoid_duplicate=""):
        assert not exclude_setting or type(exclude_setting) in [str, collections.OrderedDict]
        assert type(remap_setting) in [str, collections.OrderedDict]
        assert type(avoid_duplicate) is str

        def mature_filename(name):
            return "mature_" + name + ".txt"

        def immature_filename(name):
            return "immature_" + name + ".txt"

        self.mature_file = mature_filename(name)
        self.immature_file = immature_filename(name)
        [self.uncond_exclude_setting, self.exclude_setting] = PostAnalysis.parse_exclude_setting(exclude_setting) \
            if exclude_setting and len(exclude_setting) > 0 else [None, None]
        [self.uncond_remap_dict, self.remap_dict] = PostAnalysis.parse_remap_setting(remap_setting) \
            if len(remap_setting) > 0 else [None, None]
        self.avoid_duplicate = avoid_duplicate

    @staticmethod
    def parse_exclude_file(exclude_file, setting):
        if not os.path.exists(exclude_file):
            logging.warning("[analyzer] exclude_file \"%s\" does not exist" % exclude_file)
            return
        with open(exclude_file, 'r') as fd:
            for line in fd.readlines():
                line_str = line.replace("\n", "")
                setting[line_str] = 1  # 1 is a dummy value

    @staticmethod
    def parse_exclude_setting(exclude_setting):
        ret_setting = {}
        if type(exclude_setting) is str:  # it shall be an exclude file
            exclude_file = exclude_setting
            PostAnalysis.parse_exclude_file(exclude_file, ret_setting)
            return [ret_setting, None]
        assert isinstance(exclude_setting, collections.OrderedDict)
        for exclude_variant in exclude_setting:
            exclude_dict = exclude_setting[exclude_variant]
            assert isinstance(exclude_dict, collections.OrderedDict)
            for exclude_entry in exclude_dict:
                exclude_file = exclude_dict[exclude_entry]
                if not os.path.exists(exclude_file):
                    logging.warning("[analyzer] exclude_file \"%s\" does not exist" % exclude_file)
                    continue
                if exclude_variant not in ret_setting:
                    ret_setting[exclude_variant] = {}
                if exclude_entry not in ret_setting[exclude_variant]:
                    ret_setting[exclude_variant][exclude_entry] = {}
                PostAnalysis.parse_exclude_file(exclude_file, ret_setting[exclude_variant][exclude_entry])
        return [None, ret_setting]

    @staticmethod
    def get_remap_dict(remap_csv):
        if not os.path.exists(remap_csv):
            logging.warning("[analyzer] remap_file \"%s\" does not exist" % remap_csv)
            return None
        remap_dict = collections.OrderedDict()
        with open(remap_csv, 'r') as fd:
            import csv
            for line in csv.reader(fd):
                assert 2 == len(line)
                remap_dict[line[0].strip()] = line[1].strip()
        return remap_dict

    @staticmethod
    def parse_remap_setting(remap_setting):
        if isinstance(remap_setting, collections.OrderedDict):
            remap_dict = collections.OrderedDict()
            for variant_entry in remap_setting:
                if variant_entry not in remap_dict:
                    remap_dict[variant_entry] = collections.OrderedDict()
                remap_values = remap_setting[variant_entry]
                assert isinstance(remap_values, collections.OrderedDict)
                for variant_value in remap_values:
                    remap_file = remap_values[variant_value]
                    remap_dict[variant_entry][variant_value] = PostAnalysis.get_remap_dict(remap_file)
            return [None, remap_dict]
        assert type(remap_setting) is str
        uncond_remap_dict = PostAnalysis.get_remap_dict(remap_setting)
        return [uncond_remap_dict, None]

    @staticmethod
    def is_timed_data(data):
        if not data:
            return False
        for src_key in data:
            check_data = data[src_key]
            if not 2 == len(check_data):
                return False
            if "new" not in check_data:
                return False
            if "old" not in check_data:
                return False
        return True

    @staticmethod
    def get_remap_src_key_data(remap_spec, src_key, time_str, timed_data):
        assert time_str in ["new", "old"]
        src_key_data = collections.OrderedDict()
        for data in timed_data[src_key][time_str]:
            has_remap = False
            assert type(data) in [collections.OrderedDict, str]
            if type(data) is str:
                entry_key = data
            else:
                entry_key = list(data.items())[0][1]  # currently, we only support use first parsed value do re-map
            for remap_entry in remap_spec:
                if remap_entry in entry_key:
                    if not remap_spec[remap_entry] in src_key_data:
                        src_key_data[remap_spec[remap_entry]] = []
                    src_key_data[remap_spec[remap_entry]].append(data)
                    has_remap = True
                    break
            if not has_remap:
                default_entry = remap_spec["default"] if "default" in remap_spec else "default"
                if default_entry not in src_key_data:
                        src_key_data[default_entry] = []
                src_key_data[default_entry].append(data)
        return src_key_data

    def get_remap_spec(self, src_key):
        if self.uncond_remap_dict:
            return self.uncond_remap_dict

        assert self.remap_dict
        assert type(src_key) is tuple
        for key_entry in src_key:
            if key_entry[0] in self.remap_dict:
                remap_variant = self.remap_dict[key_entry[0]]
                if key_entry[1] in remap_variant:
                    remap_setting = remap_variant[key_entry[1]]
                    assert isinstance(remap_setting, collections.OrderedDict)
                    return remap_setting
        return None

    def remap(self, timed_data):
        if 0 == len(timed_data) or (not self.uncond_remap_dict and not self.remap_dict):
            return timed_data

        assert PostAnalysis.is_timed_data(timed_data), len(timed_data)
        remap_data = collections.OrderedDict()
        for src_key in timed_data:
            src_key_data = collections.OrderedDict()
            remap_spec = self.get_remap_spec(src_key)
            if not remap_spec:
                remap_data[src_key] = timed_data[src_key]
                continue
            src_key_data["new"] = PostAnalysis.get_remap_src_key_data(remap_spec, src_key, "new", timed_data)
            src_key_data["old"] = PostAnalysis.get_remap_src_key_data(remap_spec, src_key, "old", timed_data)
            remap_data[src_key] = src_key_data
        return remap_data

    @staticmethod
    def get_serialized_str(key, data, info_entry):
        if info_entry and type(data) is collections.OrderedDict:
            import copy
            stripped_data = copy.deepcopy(data)
            for info in info_entry:
                stripped_data.pop(info, None)
            data_str = str(stripped_data)
        else:
            data_str = str(data)
        key_str = "" if 0 == len(key) else str(key) + " => "
        return key_str + data_str

    @staticmethod
    def get_list_data(filename):
        if not os.path.exists(filename):
            return []
        list_data = []
        with open(filename, 'r') as fd:
            for line_str in fd.readlines():
                list_data.append(line_str[0:len(line_str) - 1])  # remove the end_line char
        return list_data

    @staticmethod
    def serialize_timed_data(filename, time_key, timed_data, info_entry, always_update):
        if not always_update and os.path.exists(filename) and file_modified_today(filename):
            return
        with open(filename, 'w') as fd:
            for src_key in timed_data:
                for data in timed_data[src_key][time_key]:
                    assert type(data) in [collections.OrderedDict, str]
                    fd.write(PostAnalysis.get_serialized_str(src_key, data, info_entry) + "\n")

    @staticmethod
    def is_duplicated_in_timed_data(data, timed_data, time_str):
        for src_key in timed_data:
            src_key_data = timed_data[src_key]
            assert time_str in src_key_data, time_str
            aware_data = src_key_data[time_str]
            assert type(aware_data) in [list, collections.OrderedDict]
            if type(aware_data) is list:
                for one_data in aware_data:
                    assert type(one_data) in [str, collections.OrderedDict]
                    if one_data == data:
                        return True
            else:
                for one_entry in aware_data:
                    one_data_list = aware_data[one_entry]
                    assert type(one_data_list) is list
                    for one_data in one_data_list:
                        assert type(one_data) is collections.OrderedDict
                        if one_data == data:
                            return True
        return False

    def is_duplicated(self, data, notify_data):
        if 0 == len(self.avoid_duplicate):
            return False
        if self.avoid_duplicate not in notify_data:
            logging.warning("[analyzer] avoid duplicate target \"%s\" does not exist!" % self.avoid_duplicate)
            return False
        aware_data = notify_data[self.avoid_duplicate]
        if 0 == len(aware_data):
            return False
        assert PostAnalysis.is_timed_data(aware_data)
        return PostAnalysis.is_duplicated_in_timed_data(data, aware_data, "new") or \
            PostAnalysis.is_duplicated_in_timed_data(data, aware_data, "old")

    def exclude(self, data_to_be_excluded):
        if not self.uncond_exclude_setting and not self.exclude_setting:
            return
        is_uncond_exclude = self.uncond_exclude_setting is not None
        assert is_uncond_exclude or self.exclude_setting
        for entry in data_to_be_excluded:
            assert type(entry) is tuple
            if 0 == len(entry) and is_uncond_exclude:
                exclude_list = []
                value_list = data_to_be_excluded[entry]
                for value in value_list:
                    if value in self.uncond_exclude_setting:
                        exclude_list.append(value)
                for value in exclude_list:
                    value_list.remove(value)
                data_to_be_excluded[entry] = value_list
                continue
            for src_key in entry:
                assert type(src_key) is tuple
                if is_uncond_exclude or src_key[0] in self.exclude_setting:
                    exclude_variant = None if is_uncond_exclude else self.exclude_setting[src_key[0]]
                    if is_uncond_exclude or src_key[1] in exclude_variant:
                        exclude_setting = self.uncond_exclude_setting if is_uncond_exclude \
                          else exclude_variant[src_key[1]]
                        value_list = data_to_be_excluded[entry]
                        assert type(value_list) is list
                        exclude_list = []
                        for value in value_list:
                            if value in exclude_setting:
                                exclude_list.append(value)
                        for value in exclude_list:
                            value_list.remove(value)
                        data_to_be_excluded[entry] = value_list

    def analyze(self, raw_data, notify_data, info_entry=None):
        assert type(raw_data) is collections.OrderedDict

        # filter by exclude list
        self.exclude(raw_data)

        # retrieve old result
        old_data = PostAnalysis.get_list_data(self.mature_file)
        if os.path.exists(self.immature_file) and not file_modified_today(self.immature_file):
            # immature data will read once a day, afterwards, it goes to mature data, which also write once a day
            old_data += PostAnalysis.get_list_data(self.immature_file)

        timed_data = collections.OrderedDict()
        for src_key in raw_data:
            timed_data[src_key] = collections.OrderedDict()
            timed_data[src_key]["new"] = []
            timed_data[src_key]["old"] = []
            for data in raw_data[src_key]:
                if self.is_duplicated(data, notify_data):
                    continue
                time_key = "old" if PostAnalysis.get_serialized_str(src_key, data, info_entry) in old_data else "new"
                timed_data[src_key][time_key].append(data)

        # update old result (keep the result valid within one day duration)
        #   mature data write once a day
        PostAnalysis.serialize_timed_data(self.mature_file, "old", timed_data, info_entry, False)
        #   immature data always update
        PostAnalysis.serialize_timed_data(self.immature_file, "new", timed_data, info_entry, True)

        return self.remap(timed_data)  # Note: must be done after new/old differentiation

    @staticmethod
    def create(name, data):
        if not data:
            return PostAnalysis(name)
        assert isinstance(data, dict)
        exclude_setting = {}
        remap_setting = ""
        avoid_duplicate = ""
        for entry in data:
            if entry == EXCLUDE_KEY:
                exclude_setting = data[EXCLUDE_KEY]
            elif entry == REMAP_KEY:
                remap_setting = data[REMAP_KEY]
            elif entry == AVOID_DUP_KEY:
                avoid_duplicate = data[AVOID_DUP_KEY]
            else:
                logging.warning("[post_analysis] unknown item \"%s\"" % entry)
        return PostAnalysis(name, exclude_setting, remap_setting, avoid_duplicate)

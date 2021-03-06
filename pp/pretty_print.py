#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections


def get_beautiful_value(value, show_full_data):
    assert type(value) in [collections.OrderedDict, str]
    if type(value) is str:
        return value
    if not show_full_data:
        return list(value.items())[0][1]
    ret_str = ""
    data_len = len(list(value.items()))
    for i in range(data_len):
        if i > 0:
            ret_str += '\t\t'
        ret_str += "%(name)s: %(value)s\n" % {'name': list(value.items())[i][0], 'value': list(value.items())[i][1]}
    return ret_str


def has_actual_timed_data(timed_data):
    assert isinstance(timed_data, collections.OrderedDict)
    assert "new" in timed_data
    if len(timed_data["new"]) > 0:
        return True
    assert "old" in timed_data
    if len(timed_data["old"]) > 0:
        return True
    return False


def get_beautiful_data(data, show_full_data=False):
    assert type(data) is collections.OrderedDict
    pp_data = ""
    for notify_name in data:
        pp_data += "=================================================================\n"
        pp_data += ("notification: %s\n" % notify_name)
        pp_data += "=================================================================\n"
        notify_data = data[notify_name]
        for source_key in notify_data:
            timed_data = notify_data[source_key]
            assert type(timed_data) is collections.OrderedDict
            if not has_actual_timed_data(timed_data):
                continue
            if len(source_key) > 0:
                pp_data += (str([key_value_pair[1] for key_value_pair in source_key]) + "\n")
            for iter_new_old in timed_data:
                one_time_data = timed_data[iter_new_old]
                if not one_time_data:
                    continue
                if type(one_time_data) is list:
                    pp_data += "%s (%i)\n" % (iter_new_old, len(one_time_data))
                    for entry in one_time_data:
                        entry_str = get_beautiful_value(entry, show_full_data)
                        pp_data += ("\t" + entry_str + "\n")
                elif isinstance(one_time_data, collections.OrderedDict):
                    pp_data += "%s (%i)\n" % (iter_new_old,
                                              sum([len(one_time_data[map_target]) for map_target in one_time_data]))
                    # shall be a re-mapped entry
                    for map_target in one_time_data:
                        map_data_list = one_time_data[map_target]
                        pp_data += "\t%s (%i)\n" % (map_target, len(map_data_list))
                        assert type(map_data_list) is list
                        for entry in map_data_list:
                            assert type(entry) in [collections.OrderedDict, str]
                            if type(entry) is str:
                                entry_str = entry
                            else:
                                entry_str = get_beautiful_value(entry, show_full_data)
                            pp_data += ("\t\t" + entry_str + "\n")
                else:
                    assert False
    return pp_data


def get_beautiful_pre_json(data):
    assert type(data) is collections.OrderedDict
    pre_json = collections.OrderedDict()
    for notify_name in data:
        if notify_name not in pre_json:
            pre_json[notify_name] = []
        notify_data = data[notify_name]
        for source_key in notify_data:
            assert type(source_key) is tuple
            keys = collections.OrderedDict()
            for key_entry in source_key:
                assert 2 == len(key_entry)
                keys[key_entry[0]] = key_entry[1]
            values = notify_data[source_key]
            one_src_key_entry = collections.OrderedDict()
            one_src_key_entry["key"] = keys
            one_src_key_entry["value"] = values
            pre_json[notify_name].append(one_src_key_entry)
    return pre_json

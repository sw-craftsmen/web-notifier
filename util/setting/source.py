#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import logging


PATH_KEY = "path"
VARIANT_KEY = "variant"


# ref. http://stackoverflow.com/questions/21791966/how-do-i-create-a-recursion-of-multiple-for-loops-of-lists-in-python-to-get-comb
def combinations(rest, prefix, result):
    if rest:
        first = rest.pop()
        for item in first:
            prefix.append(item)
            combinations(rest, prefix, result)
            prefix.pop()
        rest.append(first)
    else:
        result.append(list(prefix))
    return result


class Source(object):
    def __init__(self, path, variant=None):
        assert path and isinstance(path, str)
        self.perm_path = path
        self.variant = variant
        logging.debug("[source] path=%s" % self.perm_path)
        if self.variant:
            for entry in self.variant:
                variant_data = self.variant[entry]
                assert isinstance(variant_data, list) or isinstance(variant_data, dict)
                if isinstance(variant_data, list):
                    assert "$" + entry in self.perm_path
                else:
                    for grouped_variant in variant_data:
                        grouped_data = variant_data[grouped_variant]
                        assert isinstance(grouped_data, dict)
                        for grouped_entry in grouped_data:
                            assert isinstance(grouped_entry, str)
                            # note: only support at most 2-level dict variant (the leaf data must be of primitive type)
                            assert type(grouped_data[grouped_entry]) in [str, int, float]
                            assert "$" + grouped_entry in self.perm_path
        self.path = self.__gen_path()

    def __iter__(self):
        return self

    def __next__(self):
        return self.path.__next__()

    def get_digest_entry(self, entry):
        assert type(entry) is collections.OrderedDict
        for variant_entry in self.variant:
            variant_data = self.variant[variant_entry]
            if isinstance(variant_data, list):
                continue
            for grouped_variant in variant_data:
                grouped_data = variant_data[grouped_variant]
                assert isinstance(grouped_data, collections.OrderedDict)
                all_match = True
                for grouped_entry in grouped_data:
                    assert grouped_entry in entry, entry
                    if entry[grouped_entry] != grouped_data[grouped_entry]:
                        all_match = False
                        break
                if all_match:
                    # print("matched %s" % grouped_variant, entry)
                    for grouped_entry in grouped_data:
                        entry.pop(grouped_entry, None)
                        entry[variant_entry] = grouped_variant
                    break
        return entry

    def __gen_path(self):
        if not self.variant:
            empty_keys = collections.OrderedDict()
            return iter([[empty_keys, self.perm_path]])
        iter_list = []
        for entry in self.variant:
            variant_data = self.variant[entry]
            one_list = []
            if isinstance(variant_data, list):
                for inner_entry in variant_data:
                    entry_dict = {entry: inner_entry}
                    one_list.append(entry_dict)
            else:  # dict
                for grouped_variant in variant_data:
                    grouped_data = variant_data[grouped_variant]
                    entry_dict = collections.OrderedDict()
                    for grouped_entry in grouped_data:
                        entry_dict[grouped_entry] = grouped_data[grouped_entry]
                    one_list.append(entry_dict)
            iter_list.append(one_list)

        flattened_keys = []
        combined_keys = combinations(list(reversed(iter_list)), [], [])
        for entry in combined_keys:
            assert isinstance(entry, list)
            flattened_entry = collections.OrderedDict()
            for dict_item in entry:
                assert isinstance(dict_item, dict)
                for key in dict_item:
                    flattened_entry[key] = dict_item[key]
            flattened_keys.append(flattened_entry)
        key_and_path = []
        for entry in flattened_keys:
            substituted_path = self.perm_path
            for key in entry:
                substituted_path = substituted_path.replace("$" + key, str(entry[key]))
            digest_entry = self.get_digest_entry(entry)
            key_and_path.append([digest_entry, substituted_path])
        return iter(key_and_path)

    @staticmethod
    def create(data):
        assert isinstance(data, dict) or isinstance(data, str)

        if isinstance(data, str):
            path = data
            variant = None
        else:
            path = data[PATH_KEY] if PATH_KEY in data else None
            assert path
            variant = data[VARIANT_KEY] if VARIANT_KEY in data else None
        return Source(path, variant)

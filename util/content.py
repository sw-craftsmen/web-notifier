#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from web_fetch.fetcher import get_web_page


def get_content(path, username, password):
    if "http" in path:
        return get_web_page(path, username, password)
    import os
    if os.path.isfile(path):
        return path
    assert False, "path \"%s\" is not reachable" % path

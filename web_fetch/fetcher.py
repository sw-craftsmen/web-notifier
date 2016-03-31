#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
from subprocess import Popen, PIPE

HTML_FILE_NAME = "retrieved_page.html"


def get_web_content(url, login, password):
    return __get_html_lines(url, login, password)


def get_web_page(url, login, password):
    return __get_html(url, login, password)


def locate_abs_exec(program):  # 'program' can be an absolute path name, or just a basename
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


# keep the 'wget' routine as somehow we may possibly still need it?
def __get_html_by_wget(url, out_file, web_login,  web_password):
    wget_abs_path = locate_abs_exec("wget")
    if not wget_abs_path:
        logging.error("wget is required but does not present, program exits")
        sys.exit()
    output, error = Popen([wget_abs_path, "-O", out_file, web_login, web_password, url],
                          stdout=PIPE, stderr=PIPE).communicate()
    logging.info(output + error)


def __get_html_content(url, out_file, web_login,  web_password):
    import urllib.request
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, url, web_login, web_password)
    auth_handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(auth_handler)
    urllib.request.install_opener(opener)

    try:
        web_content = urllib.request.urlopen(url)
    except urllib.error.URLError as e:
        logging.error(str(e))
        return False

    with open(out_file, 'wb') as write_fd:
        write_fd.write(web_content.read().decode('big5', 'ignore').encode('utf-8'))
    return True


#
# Retrieve web content
#
def __get_html_lines(url, login, password):

    if not __get_html_content(url, HTML_FILE_NAME, login, password):
        logging.error("[retriever] cannot open url: " + url)
        return {}

    with open(HTML_FILE_NAME, "r") as html_fp:
        html_lines = html_fp.readlines()
    return html_lines


def __get_html(url, login, password):

    if not __get_html_content(url, HTML_FILE_NAME, login, password):
        logging.error("[retriever] cannot open url: " + url)
        return None

    return HTML_FILE_NAME  # TODO: use encoded file name

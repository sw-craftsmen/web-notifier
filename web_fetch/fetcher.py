#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
from subprocess import Popen, PIPE

HTML_FILE_NAME = "wget.html"


def get_web_content(url, login, password):
    return __get_html_lines(url, login, password, for_test=True)


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


#
# Call wget to retrieve web content 
#
def __get_html_lines(url, login, password, for_test):
    html_lines = {}
 
    web_login = ''
    web_password = ''
    if login:
        web_login = "--user=" + login
    if password:
        web_password = "--password=" + password

    effective_url = url if not for_test else "http://www.grymoire.com/Unix/Quote.html"

    wget_abs_path = locate_abs_exec("wget")
    if not wget_abs_path:
        logging.error("wget is required for web-notifier but does not present, program exits")
        sys.exit()
    output, error = Popen([wget_abs_path, "-O", HTML_FILE_NAME, web_login, web_password, effective_url],
            stdout=PIPE, stderr=PIPE).communicate()

    logging.info(output + error)

    with open(HTML_FILE_NAME, "r") as html_fp:
        html_lines = html_fp.readlines()
    return html_lines


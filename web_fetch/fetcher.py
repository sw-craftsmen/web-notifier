#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from subprocess import Popen, PIPE

HTML_FILE_NAME = "wget.html"

def get_web_content(url, login, password):
    return __get_html_lines(url, login, password, for_test=True)

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

    output, error = Popen(["wget", "-O", HTML_FILE_NAME, web_login, web_password, effective_url], 
            stdout=PIPE, stderr=PIPE).communicate()

    logging.info(output + error)

    with open(HTML_FILE_NAME, "r") as html_fp:
        html_lines = html_fp.readlines()
    return html_lines


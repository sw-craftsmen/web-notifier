#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

HTML_FILE_NAME = "retrieved_page.html"


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
        return False, str(e)

    with open(out_file, 'wb') as write_fd:
        # TODO: may need read html charSet to decide decode lang...
        write_fd.write(web_content.read())  # .decode('big5', 'ignore').encode('utf-8'))
    return True, ""


def __get_html(url, login, password):
    res, msg = __get_html_content(url, HTML_FILE_NAME, login, password)
    if not res:
        wget_path = locate_abs_exec("wget")
        if not wget_path:
            logging.error("[retriever] cannot open url: %s (%s)" % (url, msg))
            return None

        from subprocess import Popen, PIPE, STDOUT
        wget = Popen([wget_path, url, '--user', login, '--password', password, '-O', HTML_FILE_NAME],
                     stdout=PIPE, stderr=STDOUT)
        stdout_data, stderr_data = wget.communicate()
        if not os.path.exists(HTML_FILE_NAME) or not os.stat(HTML_FILE_NAME).st_size > 0:
            logging.error("[retriever] \'wget\': fail to fetch page (%s, %s)" % (stdout_data, stderr_data))
            return None

    return HTML_FILE_NAME

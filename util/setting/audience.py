#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import collections
import logging


SENDER_KEY = "sender"
RECEIVER_KEY = "receivers"
TITLE_KEY = "title"


class Audience(object):
    def __init__(self, sender=None, receivers=None, title=None):
        assert not sender or (type(sender) is list and 2 == len(sender))
        assert not receivers or type(receivers) is list
        [self.sender_name, self.sender_addr] = sender if sender else [None, None]
        self.receivers = receivers
        self.title = Audience.get_title_str(title)

    @staticmethod
    def get_title_str(raw_title):
        if not raw_title:
            return "Web-Notifier message"
        if '`' not in raw_title:
            return raw_title
        pre_key = '`('
        pos_pre_key = raw_title.find(pre_key)
        if -1 == pos_pre_key:
            return raw_title
        post_key = ')'
        pos_post_key = raw_title[pos_pre_key + len(pre_key):].find(post_key)
        if -1 == pos_post_key:
            return raw_title
        var_start_pos = pos_pre_key + len(pre_key)
        var_str = raw_title[var_start_pos:var_start_pos + pos_post_key]
        if "date" == var_str:
            from datetime import date
            return raw_title.replace(pre_key + var_str + post_key, str(date.today()))
        return raw_title  # unrecognized var, do nothing

    def send_mail(self, name, addr, data):
        import smtplib
        try:
            smtp_obj = smtplib.SMTP('localhost')  # we might need support specifying smtp server by configuration
        except (OSError, ConnectionRefusedError) as e:
            logging.error("[error] smtp service not available: %s", e)
            return
        receiver = ['%s' % addr]
        from email.mime.text import MIMEText
        content = MIMEText(data.replace("\n", "\t\n"), _charset='UTF-8')  # add '\t' for outlook sometimes remove '\n'
        message = "From %(sender1)s by %(sender2)s\nTo: %(receiver)s\nSubject: %(title)s\n%(content)s" \
                  % {'sender1': "WbNt", 'sender2': self.sender_name, 'receiver': name,
                     'title': self.title, 'content': content}
        pos_sender_domain = self.sender_addr.find('@')
        assert -1 != pos_sender_domain
        sender_domain = self.sender_addr[pos_sender_domain:]
        decorated_sender_addr = self.sender_name.replace(' ', '_') + "_by_WbNt" + sender_domain
        try:
            smtp_obj.sendmail(decorated_sender_addr, receiver, message)
            logging.info("[notify] successfully sent notification")
        except smtplib.SMTPException as e:
            logging.error("[error] unable to send mail: %s", e)

    def notify(self, data):
        if not self.receivers:
            return
        for [name, addr] in self.receivers:
            logging.debug("[notify] send mail to '%s':'%s'" % (name, addr))
            self.send_mail(name, addr, data)

    @staticmethod
    def create(data):
        if not data:
            return Audience()
        assert type(data) is collections.OrderedDict
        sender = None  # [name, addr]
        receivers = None  # [[name_1, addr_1], [name_2, addr_2], ..., [name_n, addr_n]]
        title = None
        for entry in data:
            if entry == SENDER_KEY:
                sender = data[SENDER_KEY]
            elif entry == RECEIVER_KEY:
                receivers = data[RECEIVER_KEY]
            elif entry == TITLE_KEY:
                title = data[TITLE_KEY]
            else:
                logging.warning("[audience] unknown item \"%s\"" % entry)
        return Audience(sender, receivers, title)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging


class Audience(object):
    def __init__(self, name_addr_list=None):
        self.name_addr_list = name_addr_list

    @staticmethod
    def send_mail(name, addr, data):
        import smtplib
        sender = 'web-notifier@github.sw-craftsmen'
        receiver = ['%s' % addr]
        message = "From %(sender)s\nTo: %(receiver)s\nSubject: %(title)s\n%(content)s" \
                  % {'sender': "WbNt", 'receiver': name, 'title': "WbNt notification", 'content': data}
        try:
            smtp_obj = smtplib.SMTP('localhost')
        except ConnectionRefusedError as e:
            logging.error("[notify] smtp service not available: %s", e)
            return
        try:
            smtp_obj.sendmail(sender, receiver, message)
            logging.info("[notify] successfully sent notification")
        except smtplib.SMTPException as e:
            logging.error("[notify] unable to send mail: %s", e)

    def notify(self, data):
        for [name, addr] in self.name_addr_list:
            logging.debug("[notify] send mail to '%s':'%s'" % (name, addr))
            Audience.send_mail(name, addr, data)

    @staticmethod
    def create(data):
        assert not data or type(data) is list
        return Audience(data)

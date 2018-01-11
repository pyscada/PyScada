# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#from pyscada.models import Log
from datetime import datetime
from django.conf import settings
import sys


def add(message, level=0, user=None, message_short=None,log_file_name='%s/pyscada_daemon.log' % settings.BASE_DIR,):
    """
    add a new massage/error notice to the log
    <0 - Debug
    1 - Emergency
    2 - Critical
    3 - Errors
    4 - Alerts
    5 - Warnings
    6 - Notification (webnotice)
    7 - Information (webinfo)
    8 - Notification (notice)
    9 - Information (info)

    """
    #if not access(path.dirname(self.log_file_name), W_OK):
    #    self.stderr.write("logfile path is not writeable\n")
    #    sys.exit(0)
    #if access(self.log_file_name, F_OK) and not access(self.log_file_name, W_OK):
    #    self.stderr.write("logfile is not writeable\n")
    #    sys.exit(0)

    if message_short is None:
        message_len = len(message)
        if message_len > 35:
            message_short = message[0:31] + '...'
        else:
            message_short = message

    #log_ob = Log(message=message, level=level, message_short=message_short, timestamp=time())
    #if user:
    #    log_ob.user = user
    #log_ob.save()
    stdout = open(log_file_name, "a+")
    stdout.write("%s (%s,%d):%s\n" % (datetime.now().isoformat(b' '),'none',level,message))
    stdout.flush()

def debug(message, level=1, user=None, message_short=None):
    add(message, -level, user, message_short)


def emerg(message, user=None, message_short=None):
    add(message, 1, user, message_short)


def crit(message, user=None, message_short=None):
    add(message, 2, user, message_short)


def error(message, user=None, message_short=None):
    add(message, 3, user, message_short)


def alert(message, user=None, message_short=None):
    add(message, 4, user, message_short)


def warning(message, user=None, message_short=None):
    add(message, 5, user, message_short)


def webnotice(message, user=None, message_short=None):
    add(message, 6, user, message_short)


def webinfo(message, user=None, message_short=None):
    add(message, 7, user, message_short)


def notice(message, user=None, message_short=None):
    add(message, 8, user, message_short)


def info(message, user=None, message_short=None):
    add(message, 9, user, message_short)

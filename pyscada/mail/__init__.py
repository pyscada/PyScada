#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import Process as BaseProcess
from pyscada.models import Mail
from time import time


class Process(BaseProcess):
    def loop(self):
        """
        check for mails and send them
        """
        for mail in Mail.objects.filter(done=False, send_fail_count__lt=3):
            # send all emails that are not already send or failed to send less 
            # then three times
            mail.send_mail()

        for mail in Mail.objects.filter(done=True, timestamp__lt=time() - 60 * 60 * 24 * 7):
            # delete all done emails older then one week
            mail.delete()

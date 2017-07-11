#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pyscada.models import Event
from pyscada.utils.scheduler import Process as BaseProcess


class Process(BaseProcess):
    def loop(self):
        """
        check for events and trigger action
        """
        for item in Event.objects.all():
            item.do_event_check()

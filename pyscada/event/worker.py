#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Event
from pyscada.utils.scheduler import Process as BaseProcess
import logging

logger = logging.getLogger(__name__)


class Process(BaseProcess):
    def __init__(self, dt=5, **kwargs):
        super(Process, self).__init__(dt=dt, **kwargs)
    def loop(self):
        """
        check for events and trigger actions
        """
        for item in Event.objects.all():
            item.do_event_check()

        return 1, None

#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pyscada.models import Event


class Handler:
    def __init__(self):
        """
        init the handler
        """
        self.dt_set = 5

    def run(self):
        """
        check for events and trigger action
        """
        for item in Event.objects.all():
            item.do_event_check()

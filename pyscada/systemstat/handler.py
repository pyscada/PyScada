#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyscada.models import Client
from pyscada.models import RecordedTime

from pyscada.systemstat.client import Client as SystemStatClient

from django.conf import settings

from time import time

class Handler:
    def __init__(self):
        if settings.PYSCADA_SYSTEMSTAT.has_key('polling_interval'):
            self.dt_set = float(settings.PYSCADA_SYSTEMSTAT['polling_interval'])
        else:
            self.dt_set = 5 # default value is 5 seconds
        self._clients   = {}
        self._prepare_clients()

    def run(self):
        """
            request data
        """
        ## data acquisition
        timestamp = RecordedTime(timestamp=time())
        timestamp.save()
        data = []
        for idx in self._clients:
            data += self._clients[idx].request_data(timestamp)
        
        return data
    
    def _prepare_clients(self):
        """
        prepare clients for query
        """
        for item in Client.objects.filter(active=1):
            if item.client_type == 'systemstat':
                self._clients[item.pk] = SystemStatClient(item)
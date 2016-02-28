#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyscada.models import Device
from pyscada.models import RecordedTime

from pyscada.systemstat.device import Device as SystemStatDevice

from django.conf import settings

from time import time

class Handler:
    def __init__(self):
        if settings.PYSCADA_SYSTEMSTAT.has_key('polling_interval'):
            self.dt_set = float(settings.PYSCADA_SYSTEMSTAT['polling_interval'])
        else:
            self.dt_set = 5 # default value is 5 seconds
        self._devices   = {}
        self._prepare_devices()

    def run(self,timestamp=None):
        """
            request data
        """
        ## data acquisition
        if timestamp is None:
            timestamp = time()
        data = []
        for idx in self._devices:
            data += self._devices[idx].request_data(timestamp)
        
        return data
    
    def _prepare_devices(self):
        """
        prepare devices for query
        """
        for item in Device.objects.filter(active=1):
            if item.device_type == 'systemstat':
                self._devices[item.pk] = SystemStatDevice(item)
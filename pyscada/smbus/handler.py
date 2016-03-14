#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyscada.models import Device
from pyscada.models import RecordedTime

from pyscada.smbus.device import Device as SMBusDevice

from django.conf import settings

from time import time

class Handler:
    def __init__(self):
        
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
            if item.device_type == 'smbus':
                self._devices[item.pk] = SMBusDevice(item)
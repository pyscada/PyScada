# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

try:
    import visa
    driver_visa_ok = True
except ImportError:
    driver_visa_ok = False

from time import time
import logging

logger = logging.getLogger(__name__)


class Device:
    def __init__(self, device):
        self.variables = {}
        self.device = device
        if self.device.visadevice.instrument.handler_path is not None:
            sys.path.append(self.device.visadevice.instrument.handler_path)
        try:
            mod = __import__(self.device.visadevice.instrument.handler_class, fromlist=['Handler'])
            device_handler = getattr(mod, 'Handler')
            self._h = device_handler(self.device, self.variables)
            driver_handler_ok = True
        except ImportError:
            driver_handler_ok = False
            
        for var in self.device.variable_set.filter(active=1):
            if not hasattr(var, 'visavariable'):
                continue
            self.variables[var.pk] = var
        
        if driver_visa_ok and driver_handler_ok:
            self._h.connect()

    def write_data(self, variable_id, value, task):
        return self._h.write_data(variable_id, value, task)

    def request_data(self):
        """
        request data from the instrument/device
        """
        output = []
        if not driver_visa_ok:
            return output
        
        for item in self.variables.values():
            if not item.visavariable.variable_type == 1:
                # skip all config values
                continue
            
            value = self._h.read_data(item)
            
            if value is not None and item.update_value(value, time()):
                output.append(item.create_recorded_data_element())
        
        return output

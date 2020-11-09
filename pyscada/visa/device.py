# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

try:
    import pyvisa
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
        if self.device.visadevice.instrument is not None \
                and self.device.visadevice.instrument.handler_path is not None:
            sys.path.append(self.device.visadevice.instrument.handler_path)
        try:
            mod = __import__(self.device.visadevice.instrument.handler_class, fromlist=['Handler'])
            device_handler = getattr(mod, 'Handler')
            self._h = device_handler(self.device, self.variables)
            driver_handler_ok = True
        except ImportError:
            driver_handler_ok = False
            logger.error("Handler import error : %s" % self.device.short_name)

        for var in self.device.variable_set.filter(active=1):
            if not hasattr(var, 'visavariable'):
                continue
            self.variables[var.pk] = var

        if driver_visa_ok and driver_handler_ok:
            self._h.connect()

    def write_data(self, variable_id, value, task):
        """
        write value to the instrument/device
        """
        output = []
        if not driver_visa_ok:
            logger.info("Cannot import visa")
            return output
        for item in self.variables.values():
            if not (item.visavariable.variable_type == 0 and item.id == variable_id):
                # skip all config values
                continue
            # read_value = self._h.write_data(item.visavariable.device_property, value)
            read_value = self._h.write_data(variable_id, value, task)
            if read_value is not None and item.update_value(read_value, time()):
                output.append(item.create_recorded_data_element())
            else:
                logger.info("Visa-Output not ok : %s" % output)
        return output

    def request_data(self):
        """
        request data from the instrument/device
        """
        output = []
        if not driver_visa_ok:
            logger.info('Cannot import visa')
            return output

        self._h.before_read()
        for item in self.variables.values():
            if not item.visavariable.variable_type == 1:
                # skip all config values
                continue

            value, time = self._h.read_data_and_time(item)

            if value is not None and item.update_value(value, time):
                output.append(item.create_recorded_data_element())
        self._h.after_read()
        return output

    def get_handler_instance(self):
        try:
            return self._h
        except AttributeError:
            return None

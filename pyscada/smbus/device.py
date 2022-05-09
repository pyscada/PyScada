# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    import smbus
    driver_ok = True
except ImportError:
    smbus = None
    driver_ok = False
import sys
from time import time
import logging

logger = logging.getLogger(__name__)


class Device:
    def __init__(self, device):
        self.variables = {}
        self.device = device
        if self.device.smbusdevice.instrument_handler is not None \
                and self.device.smbusdevice.instrument_handler.handler_path is not None:
            sys.path.append(self.device.smbusdevice.instrument_handler.handler_path)
        try:
            mod = __import__(self.device.smbusdevice.instrument_handler.handler_class, fromlist=['Handler'])
            device_handler = getattr(mod, 'Handler')
            self._h = device_handler(self.device, self.variables)
            self.driver_handler_ok = True
        except ImportError:
            self.driver_handler_ok = False
            logger.error("Handler import error : %s" % self.device.short_name)

        for var in device.variable_set.filter(active=1):
            if not hasattr(var, 'smbusvariable'):
                continue
            self.variables[var.pk] = var

    def write_data(self, variable_id, value, task):
        """
        write value to the instrument/device
        """
        output = []
        if not driver_ok:
            logger.info("Cannot import smbus")
            return output

        self._h.connect()

        for item in self.variables.values():
            if item.id != variable_id:
                continue
            # read_value = self._h.write_data(item.smbusvariable.device_property, value)
            read_value = self._h.write_data(variable_id, value, task)
            if read_value is not None and item.update_value(read_value, time()):
                output.append(item.create_recorded_data_element())
            else:
                logger.info("SMBus write data - Output not ok : %s" % output)

        self._h.disconnect()

        return output

    def request_data(self):
        """
        
        """
        output = []

        if not driver_ok or not self.driver_handler_ok:
            logger.info("Cannot import smbus or handler")
            return output

        self._h.connect()

        self._h.before_read()
        for item in self.variables.values():

            value, time = self._h.read_data_and_time(item)

            if value is not None and item.update_value(value, time):
                output.append(item.create_recorded_data_element())
        self._h.after_read()

        self._h.disconnect()

        return output

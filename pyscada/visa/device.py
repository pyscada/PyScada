# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.device import GenericDevice

try:
    import pyvisa
    driver_visa_ok = True
except ImportError:
    driver_visa_ok = False

from time import time
import logging

logger = logging.getLogger(__name__)


class Device(GenericDevice):
    def __init__(self, device):
        self.driver_ok = driver_visa_ok
        super().__init__(device)

        for var in self.device.variable_set.filter(active=1):
            if not hasattr(var, 'visavariable'):
                continue
            self.variables[var.pk] = var

        if self.driver_ok and self.driver_handler_ok:
            self._h.connect()
        else:
            logger.warning(f'Cannot import visa or handler for {self.device}')

    def write_data(self, variable_id, value, task):
        """
        write value to the instrument/device
        """
        output = []
        if not self.driver_ok:
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
                logger.info(f"Visa-Output not ok : {output}")
        return output

    def request_data(self):
        """
        request data from the instrument/device
        """
        output = []
        if not self.driver_ok:
            logger.info('Cannot import visa')
            return output

        output = super().request_data()
        return output

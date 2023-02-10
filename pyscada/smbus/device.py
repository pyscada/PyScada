# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.device import GenericDevice

from time import time
import logging

logger = logging.getLogger(__name__)

try:
    import smbus
    driver_ok = True
except ImportError:
    smbus = None
    logger.info('Cannot import smbus')
    driver_ok = False


class Device(GenericDevice):
    def __init__(self, device):
        self.driver_ok = driver_ok
        super().__init__(device)

        for var in self.device.variable_set.filter(active=1):
            if not hasattr(var, 'smbusvariable'):
                continue
            self.variables[var.pk] = var

    def write_data(self, variable_id, value, task):
        """
        write value to the instrument/device
        """
        output = []
        if not self.driver_ok:
            logger.info("Cannot import smbus")
            return output

        self._h.connect()

        if self._h.inst is None:
            return output

        output = super().write_data(variable_id, value, task)

        self._h.disconnect()

        return output

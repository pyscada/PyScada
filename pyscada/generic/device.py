# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.device import GenericDevice
from .devices import GenericDevice as GenericHandlerDevice

driver_ok = True

from time import time
import logging

logger = logging.getLogger(__name__)


class Device(GenericDevice):
    def __init__(self, device):
        self.driver_ok = driver_ok
        self.handler_class = GenericHandlerDevice
        super().__init__(device)

        for var in self.device.variable_set.filter(active=1):
            self.variables[var.pk] = var

        if self.driver_ok and self.driver_handler_ok:
            self._h.connect()
        else:
            logger.warning(f'Cannot import handler for {self.device}')

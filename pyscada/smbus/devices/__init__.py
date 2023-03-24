# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .. import PROTOCOL_ID
from pyscada.device import GenericHandlerDevice

import logging

logger = logging.getLogger(__name__)

try:
    import smbus
    driver_ok = True
except ImportError:
    smbus = None
    logger.error("Cannot import smbus")
    driver_ok = False


class GenericDevice(GenericHandlerDevice):
    def __init__(self, pyscada_device, variables):
        super().__init__(pyscada_device, variables)
        self._protocol = PROTOCOL_ID
        self.driver_ok = driver_ok

    def connect(self):
        """
        establish a connection to the Instrument
        """
        super().connect()
        result = True

        try:
            self.inst = smbus.SMBus(int(self._device.smbusdevice.port))
        except Exception as e:
            self._not_accessible_reason = e
            #logger.error(f"SMBus connect failed. Port : {self._device.smbusdevice.port} - id : {self._device.id} - "
            #             f"name {self._device.short_name}")
            result = False

        self.accessibility()
        return result

    def disconnect(self):
        if self.inst is not None:
            self.inst.close()
            self.inst = None
            return True
        return False

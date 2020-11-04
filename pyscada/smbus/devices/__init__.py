# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.conf import settings

try:
    import smbus
    driver_ok = True
except ImportError:
    smbus = None
    driver_ok = False

from time import time

import logging

logger = logging.getLogger(__name__)


class GenericDevice:
    def __init__(self, pyscada_device, variables):
        self._device = pyscada_device
        self._variables = variables
        self.inst = None

    def connect(self):
        """
        establish a connection to the Instrument
        """
        if not driver_ok:
            logger.error("SMBus driver NOT ok")
            return False

        try:
            self.inst = smbus.SMBus(int(self._device.smbusdevice.port))
        except:
            logger.error("SMBus connect failed : %s" % self)
            return False
        logger.debug('Connected SMBus device : %s' % self)
        return True

    def disconnect(self):
        if self.inst is not None:
            self.inst.close()
            self.inst = None
            return True
        return False

    def before_read(self):
        """
        will be called before the first read_data
        """
        return None

    def after_read(self):
        """
        will be called after the last read_data
        """
        return None

    def read_data(self, variable_instance):
        """
        read values from the device
        """

        return None

    def read_data_and_time(self, variable_instance):
        """
        read values and timestamps from the device
        """

        return self.read_data(variable_instance), self.time()

    def write_data(self, variable_id, value, task):
        """
        write values to the device
        """
        return False

    def time(self):
        return time()

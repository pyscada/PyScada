# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.conf import settings

try:
    import visa
    driver_ok = True
except ImportError:
    visa = None
    driver_ok = False

from time import time

import logging

logger = logging.getLogger(__name__)


class GenericDevice:
    def __init__(self, pyscada_device, variables):
        self._device = pyscada_device
        self._variables = variables
        self.inst = None
        self.rm = None

    def connect(self):
        """
        establish a connection to the Instrument
        """
        if not driver_ok:
            logger.error("Visa driver NOT ok")
            return False
        visa_backend = '@py'  # use PyVISA-py as backend
        if hasattr(settings, 'VISA_BACKEND'):
            visa_backend = settings.VISA_BACKEND

        try:
            self.rm = visa.ResourceManager(visa_backend)
        except:
            logger.error("Visa ResourceManager cannot load resources : %s" % self)
            return False
        try:
            resource_prefix = self._device.visadevice.resource_name.split('::')[0]
            extras = {}
            if hasattr(settings, 'VISA_DEVICE_SETTINGS'):
                if resource_prefix in settings.VISA_DEVICE_SETTINGS:
                    extras = settings.VISA_DEVICE_SETTINGS[resource_prefix]
            logger.debug('VISA_DEVICE_SETTINGS for %s: %r' % (resource_prefix, extras))
            self.inst = self.rm.open_resource(self._device.visadevice.resource_name, **extras)
        except:
            logger.error("Visa ResourceManager cannot open resource : %s" % self._device.visadevice.resource_name)
            return False
        logger.debug('Connected visa device : %s' % self)
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

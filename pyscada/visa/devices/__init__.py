# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .. import PROTOCOL_ID
from pyscada.models import DeviceProtocol

from django.conf import settings

try:
    import pyvisa
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

        if self._device.protocol.id != PROTOCOL_ID:
            logger.error("Wrong handler selected : it's for %s device while device protocol is %s" %
                         (str(DeviceProtocol.objects.get(id=PROTOCOL_ID)).upper(),
                          str(self._device.protocol).upper()))
            return False

        visa_backend = '@py'  # use PyVISA-py as backend
        if hasattr(settings, 'VISA_BACKEND'):
            visa_backend = settings.VISA_BACKEND

        try:
            self.rm = pyvisa.ResourceManager(visa_backend)
        except:
            logger.error("Visa ResourceManager cannot load resources : %s" % self)
            return False
        try:
            resource_prefix = self._device.visadevice.resource_name.split('::')[0]
            extras = {}
            if hasattr(settings, 'VISA_DEVICE_SETTINGS'):
                if resource_prefix in settings.VISA_DEVICE_SETTINGS:
                    extras = settings.VISA_DEVICE_SETTINGS[resource_prefix]
            self.inst = self.rm.open_resource(self._device.visadevice.resource_name, **extras)
        except Exception as e:
            logger.info(e)
            # logger.error("Visa ResourceManager cannot open resource : %s" % self._device.visadevice.resource_name)
            return False
        logger.debug('Connected visa device : %s with VISA_DEVICE_SETTINGS for %s: %r' %
                     (self._device.visadevice.resource_name, resource_prefix, extras))
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
        if self.inst is None:
            logger.error("%s has no visa instrument defined" % self)
            self.connect()
            return None
        device_property = variable_instance.visavariable.device_property.upper()
        if device_property == 'present_value'.upper():
            return self.parse_value(self.inst.query(':READ?'))
        else:
            try:
                value = self.inst.query(device_property)
            except pyvisa.errors.VisaIOError as e:
                logger.info('VisaIOError while querying value for variable %s' %variable_instance)
                value = None
            #logger.info("%s data-property : %s - value : %s" % (self, device_property, value))
            #            return value.split(',')[0]
            return self.parse_value(value, variable_instance=variable_instance)

    def read_data_and_time(self, variable_instance):
        """
        read values and timestamps from the device
        """

        return self.read_data(variable_instance), self.time()

    def write_data(self, variable_id, value, task):
        """
        write values to the device
        """
        variable = self._variables[variable_id]
        if variable.visavariable.device_property != '':
            # write the freq property to VariableProperty use that for later read
            # vp = VariableProperty.objects.update_or_create_property(variable=variable, name=task.property_name.upper(),
            #                                                        value=value, value_class='FLOAT64')
            # return True
            pass
        if variable.visavariable.variable_type == 0:  # configuration
            # only write to configuration variables
            if variable.dictionary is not None:
                value = variable.dictionary.get_label(value)
            try:
                read_value = self.inst.query(str(variable.visavariable.device_property) + ' ' + str(value))
            except pyvisa.errors.VisaIOError as e:
                read_value = None
            return self.parse_value(read_value)

        return False

    def parse_value(self, value, **kwargs):
        """
        takes a string in the Tektronix AFG1022 format and returns a float value or None if not parseable
        """
        try:
            if 'variable_instance' in kwargs:
                logger.debug(kwargs['variable_instance'])
                return float(kwargs['variable_instance'].convert_string_value(value))
            return float(value)
        except Exception as e:
            logger.debug(e)
            return None

    def time(self):
        return time()

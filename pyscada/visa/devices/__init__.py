# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .. import PROTOCOL_ID
from pyscada.models import DeviceProtocol
from pyscada.device import GenericHandlerDevice

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


class GenericDevice(GenericHandlerDevice):
    def __init__(self, pyscada_device, variables):
        super().__init__(pyscada_device, variables)
        self._protocol = PROTOCOL_ID
        self.driver_ok = driver_ok
        self.rm = None

    def connect(self):
        """
        establish a connection to the Instrument
        """
        super().connect()
        result = True

        visa_backend = '@py'  # use PyVISA-py as backend
        if hasattr(settings, 'VISA_BACKEND'):
            visa_backend = settings.VISA_BACKEND

        try:
            if self.rm is None:
                self.rm = pyvisa.ResourceManager(visa_backend)
        except:
            logger.error("Visa ResourceManager cannot load resources : %s" % self)
            result = False

        if self.rm is not None:
            try:
                resource_prefix = self._device.visadevice.resource_name.split('::')[0]
                extras = {}
                if hasattr(settings, 'VISA_DEVICE_SETTINGS'):
                    if resource_prefix in settings.VISA_DEVICE_SETTINGS:
                        extras = settings.VISA_DEVICE_SETTINGS[resource_prefix]
                if self.inst is None:
                    self.inst = self.rm.open_resource(self._device.visadevice.resource_name, **extras)

                logger.debug('Connected visa device : %s with VISA_DEVICE_SETTINGS for %s: %r' %
                             (self._device.visadevice.resource_name, resource_prefix, extras))
            except Exception as e:
                logger.info(e)
                # logger.error("Visa ResourceManager cannot open resource : %s" % self._device.visadevice.resource_name)
                result = False

        self.accessibility()
        return result

    def disconnect(self):
        if self.inst is not None:
            self.inst.close()
            self.inst = None
            return True
        return False

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

    def read_data_all(self, variables_dict):
        output = []

        self.before_read()
        for item in self._variables.values():
            if not item.visavariable.variable_type == 1:
                # skip all config values
                continue

            value, time = self.read_data_and_time(item)

            if value is not None and item.update_value(value, time):
                output.append(item.create_recorded_data_element())
        self.after_read()
        return output

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

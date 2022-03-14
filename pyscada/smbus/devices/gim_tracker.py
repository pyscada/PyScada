# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.smbus.devices import GenericDevice
from pyscada.models import VariableProperty, RecordedData
from time import time
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)


class Handler(GenericDevice):
    """
    query data via smbus (I2C) from a GIM tracker device
    """

    def read_data(self, variable_instance):
        """
        read values from the device
        """
        try:
            if variable_instance.smbusvariable.information == 'tension':
                msb = (self.inst.read_byte_data(self._device.smbusdevice.address, 0x1e)) * 16
                lsb = (self.inst.read_byte_data(self._device.smbusdevice.address, 0x1f)) / 16
                return self.parse_value((msb + lsb) * 0.025)

            elif variable_instance.smbusvariable.information == 'courant':
                msb = (self.inst.read_byte_data(self._device.smbusdevice.address, 0x14)) * 16
                lsb = (self.inst.read_byte_data(self._device.smbusdevice.address, 0x15)) / 16
                return self.parse_value((msb + lsb) * 0.0025)

            elif variable_instance.smbusvariable.information == 'energie':
                lsb = (self.inst.read_byte_data(self._device.smbusdevice.address, 0x3F))
                msb3 = (self.inst.read_byte_data(self._device.smbusdevice.address, 0x3C))
                msb2 = (self.inst.read_byte_data(self._device.smbusdevice.address, 0x3D))
                msb1 = (self.inst.read_byte_data(self._device.smbusdevice.address, 0x3E))
                return self.parse_value((lsb + msb1 * 256 + msb2 * 65536 + msb3 * 16777216) * 0.0673157)

            elif variable_instance.smbusvariable.information == 'puissance':
                lsb = (self.inst.read_byte_data(self._device.smbusdevice.address, 0x07))
                msb2 = (self.inst.read_byte_data(self._device.smbusdevice.address, 0x05))
                msb1 = (self.inst.read_byte_data(self._device.smbusdevice.address, 0x06))
                return self.parse_value((msb2 * 65536 + msb1 * 256 + lsb) * 0.0673157 / 1000.0)
                
        except OSError:
            pass

        return None

    def write_data(self, variable_id, value, task):
        """
        write values to the device
        """
        variable = self._variables[variable_id]
        if task.variable_property and task.variable_property.name != '':
            # write the freq property to VariableProperty use that for later read
            vp = VariableProperty.objects.update_or_create_property(variable=variable, name=task.property_name.upper(),
                                                                    value=value, value_class='FLOAT64')
            return True
        if variable.writeable:
            if variable.smbusvariable.information == 'raz':
                task.variable.update_value(1, time())
                item = task.variable.create_recorded_data_element()
                item.date_saved = now()
                RecordedData.objects.bulk_create([item])
                self.inst.write_byte_data(self._device.smbusdevice.address, 0x01, 2)
                self.inst.write_byte_data(self._device.smbusdevice.address, 0x01, 0)
                return self.parse_value(self.inst.read_byte_data(self._device.smbusdevice.address, 0x01))
        else:
            logger.debug("Variable %s not writeable" % variable)
            return None

    def parse_value(self, value, **kwargs):
        """
        takes a string in the HP3456A format and returns a float value or None if not parseable
        """
        try:
            return float(value)
        except:
            return None

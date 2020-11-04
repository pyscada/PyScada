# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.smbus.devices import GenericDevice


class Handler(GenericDevice):
    """
    query data via smbus (I2C) from a GIM tracker device
    """

    def read_data(self, variable_instance):
        """
        read values from the device
        """
        if variable_instance.info == 'tension':
            msb = (self.inst.read_byte_data(self._device.address, 0x1e)) * 16
            lsb = (self.inst.read_byte_data(self._device.address, 0x1f)) / 16
            return self.parse_value((msb + lsb) * 0.025)

        elif variable_instance.info == 'courant':
            msb = (self.inst.read_byte_data(self._device.address, 0x14)) * 16
            lsb = (self.inst.read_byte_data(self._device.address, 0x15)) / 16
            return self.parse_value((msb + lsb) * 0.0025)

        elif variable_instance.info == 'energie':
            lsb = (self.inst.read_byte_data(self._device.address, 0x3F))
            msb3 = (self.inst.read_byte_data(self._device.address, 0x3C))
            msb2 = (self.inst.read_byte_data(self._device.address, 0x3D))
            msb1 = (self.inst.read_byte_data(self._device.address, 0x3E))
            return self.parse_value((lsb + msb1 * 256 + msb2 * 65536 + msb3 * 16777216) * 0.0673157)

        elif variable_instance.info == 'puissance':
            lsb = (self.inst.read_byte_data(self._device.address, 0x07))
            msb2 = (self.inst.read_byte_data(self._device.address, 0x05))
            msb1 = (self.inst.read_byte_data(self._device.address, 0x06))
            return self.parse_value((msb2 * 65536 + msb1 * 256 + lsb) * 0.0673157)

        return None

    def parse_value(self, value):
        """
        takes a string in the HP3456A format and returns a float value or None if not parseable
        """
        try:
            return float(value)

        except:
            return None

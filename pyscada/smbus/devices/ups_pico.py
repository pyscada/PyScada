# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.smbus.devices import GenericDevice


class Handler(GenericDevice):
    """
    query data via smbus (I2C) from a UPS Pico  device
    """

    def read_data(self, variable_instance):
        """
        read values from the device
        """
        if variable_instance.smbusvariable.information == 'ad1':
            data = self.inst.read_word_data(self._device.smbusdevice.address, 0x05)
            data = format(data, "02x")
            return float(data) / 100  # °C

        if variable_instance.smbusvariable.information == 'ad2':
            data = self.inst.read_word_data(self._device.smbusdevice.address, 0x07)
            data = format(data, "02x")
            return float(data) / 100  # °C

        if variable_instance.smbusvariable.information == 'rpi_level':
            data = self.inst.read_word_data(self._device.smbusdevice.address, 0x03)
            data = format(data, "02x")
            return float(data) / 100  # Volt

        if variable_instance.smbusvariable.information == 'bat_level':
            data = self.inst.read_word_data(self._device.smbusdevice.address, 0x01)
            data = format(data, "02x")
            return float(data) / 100  # Volt

        if variable_instance.smbusvariable.information == 'pwr_mode':
            data = self.inst.read_word_data(self._device.smbusdevice.address, 0x00)
            return data & ~(1 << 7)  # 1 RPi, 2 Bat

        if variable_instance.smbusvariable.information == 'sot23_temp':
            data = self.inst.read_byte_data(self._device.smbusdevice.address, 0x0C)
            data = format(data, "02x")
            return data

        if variable_instance.smbusvariable.information == 'to92_temp':
            data = self.inst.read_byte_data(self._device.smbusdevice.address, 0x0D)
            data = format(data, "02x")
            return data

        return None

    def parse_value(self, value):
        """
        takes a string in the HP3456A format and returns a float value or None if not parseable
        """
        try:
            return float(value)
        except:
            return None

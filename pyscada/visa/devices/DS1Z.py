# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.visa.devices import GenericDevice

class Handler(GenericDevice):
    """
    Keithley DMM 2000 and other Devices with the same command set
    """

    def read_data(self, variable_instance):
        """
        read values from the device
        """
        if self.inst is None:
            return
        if variable_instance.visavariable.device_property.upper() == 'vrms_chan1':
            return self.parse_value(self.inst.query(':MEAS:ITEM? VRMS,CHAN1'))
        else:
            return super().read_data(variable_instance)

    def write_data(self, variable_id, value, task):
        """
        write values to the device
        """
        return super().write_data(variable_id, value, task)

    def parse_value(self, value, **kwargs):
        """
        takes a string in the Keithley DMM 2000 format and returns a float value or None if not parse able
        """
        return super().parse_value(value, **kwargs)
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.visa.devices import GenericDevice
from pyscada.models import VariableProperty


class Handler(GenericDevice):
    """
    HP3456A and other Devices with the same command set
    """

    def read_data(self,variable_instance):
        """
        read values from the device
        """
        if self.inst is None:
            return
        if variable_instance.visavariable.device_property.upper() == 'PRESENT_VALUE':
            return self.parse_value(self.inst.query('?U6P0'))
        elif variable_instance.visavariable.device_property.upper() == 'PRESENT_VALUE_DCV':
            return self.parse_value(self.inst.query('?U6P0F1T3'))
        elif variable_instance.visavariable.device_property.upper() == 'PRESENT_VALUE_ACV':
            return self.parse_value(self.inst.query('?U6P0F2T3'))
        elif variable_instance.visavariable.device_property.upper() == 'PRESENT_VALUE_DCV+ACV':
            return self.parse_value(self.inst.query('?U6P0F3T3'))
        elif variable_instance.visavariable.device_property.upper() == 'PRESENT_VALUE_2W_OHM':
            return self.parse_value(self.inst.query('?U6P0F4T3'))
        elif variable_instance.visavariable.device_property.upper() == 'PRESENT_VALUE_4W_OHM':
            return self.parse_value(self.inst.query('?U6P0F5T3'))
        else:
            return super().read_data(variable_instance)

    def write_data(self,variable_id, value, task):
        """
        write values to the device
        """
        return super().write_data(variable_id, value, task)

    def parse_value(self,value, **kwargs):
        """
        takes a string in the HP3456A format and returns a float value or None if not parseable
        """
        return super().parse_value(value, **kwargs)

# -*- coding: utf-8 -*-
from pyscada.visa.devices import GenericDevice


class Handler(GenericDevice):
    """
    HP3456A and other Devices with the same command set
    """
    
    def read_data(self,device_property):
        """
        read values from the device
        """
        if self.inst is None:
            return
        if device_property == 'present_value':
            return self.parse_value(self.inst.query('?U6P0'))
        elif device_property == 'present_value_DCV':
            return self.parse_value(self.inst.query('?U6P0F1T3'))
        elif device_property == 'present_value_ACV':
            return self.parse_value(self.inst.query('?U6P0F2T3'))
        elif device_property == 'present_value_DCV+ACV':
            return self.parse_value(self.inst.query('?U6P0F3T3'))
        elif device_property == 'present_value_2W_Ohm':
            return self.parse_value(self.inst.query('?U6P0F4T3'))
        elif device_property == 'present_value_4W_Ohm':
            return self.parse_value(self.inst.query('?U6P0F5T3'))
        return None
    
    def write_data(self,variable_id, value):
        """
        write values to the device
        """
        return False

    def parse_value(self,value):
        """
        takes a string in the HP3456A format and returns a float value or None if not parseable
        """
        try:
            return float(value)
        except:
            return None
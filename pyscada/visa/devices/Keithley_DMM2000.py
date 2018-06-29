# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.visa.devices import GenericDevice
from pyscada.models import VariableProperty


class Handler(GenericDevice):
    """
    Keithley DMM 2000 and other Devices with the same command set
    """
    
    def read_data(self,variable_instance):
        """
        read values from the device
        """
        if self.inst is None:
             return
        if variable_instance.visavariable.device_property.upper() == 'PRESENT_VALUE':
            return self.parse_value(self.inst.query(':FETCH?'))
        return None

    def write_data(self,variable_id, value, task):
        """
        write values to the device
        """
        variable = self._variables[variable_id]
        if task.property_name != '':
            # write the freq property to VariableProperty use that for later read
            vp = VariableProperty.objects.update_or_create_property(variable=variable,
                                                                    name='VISA:%s' % task.property_name.upper(),
                                                                    value=value, value_class='FLOAT64')
            return True
        return False

    def parse_value(self,value):
        """
        takes a string in the Keithley DMM 2000 format and returns a float value or None if not parse able
        """
        try:
            return float(value)
        except:
            return None

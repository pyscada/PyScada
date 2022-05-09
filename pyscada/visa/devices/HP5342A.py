# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.visa.devices import GenericDevice
from pyscada.models import VariableProperty


class Handler(GenericDevice):
    """
    HP5342A and other Devices with the same command set
    """

    def read_data(self, variable_instance):
        """
        read values from the device
        """
        if self.inst is None:
            return
        if variable_instance.visavariable.device_property.upper() == 'PRESENT_VALUE':
            return self.parse_value(self.inst.query('?U6P0'))
        elif variable_instance.visavariable.device_property.upper() == 'PRESENT_VALUE_MANUAL_C_FREQ':
            freq = VariableProperty.objects.get_property(variable=variable_instance, name='VISA:FREQ')
            if freq is None:
                freq = 500
            return self.parse_value(self.inst.query('?MAM1SR9HT3ST2SM%dE'%freq))
        else:
            return super().read_data(variable_instance)

    def write_data(self, variable_id, value, task):
        """
        write values to the device or to variable property for later read
        """
        variable = self._variables[variable_id]
        if variable.visavariable.variable_type == 0:  # configuration
            # only write to configuration variables
            if task.property_name != '':
                # write the freq property to VariableProperty use that for later read
                vp = VariableProperty.objects.update_or_create_property(variable=variable, name=task.property_name.upper(),
                                                            value=value, value_class='FLOAT64')
                return True
            else:
                return False
        else:
            return False


    def parse_value(self, value, **kwargs):
        """
        takes a string in the HP3456A format and returns a float value or None if not parseable
        """
        return super().parse_value(value, **kwargs)

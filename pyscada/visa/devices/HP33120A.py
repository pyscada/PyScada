# -*- coding: utf-8 -*-
from pyscada.visa.devices import GenericDevice
from pyscada.models import VariableProperty

import logging

logger = logging.getLogger(__name__)


class Handler(GenericDevice):
    """
    HP 33120A and other Devices with the same command set
    """

    def read_data(self, variable_instance):
        """
        read values from the device
        """
        return super().read_data(variable_instance)

    def write_data(self, variable_id, value, task):
        """
        write values to the device
        """
        return super().write_data(variable_id, value, task)

    def parse_value(self, value, **kwargs):
        """
        takes a string in the HP 33120A format and returns a float value or None if not parseable
        """
        return super().parse_value(value, **kwargs)

    # AFG functions
    def afg_prepare_for_bode(self, ch=1):
        return self.inst.query(':OUTPut:LOAD MAX;:AM:STAT OFF;*OPC?;')

    def afg_set_output_state(self, ch=1, state=True):
        return False

    def afg_set_offset(self, ch=1, offset=0):
        return self.inst.query(':VOLTage:OFFSet %s;*OPC?' % offset)

    def afg_set_vpp(self, ch=1, vpp=1):
        return self.inst.query(':VOLT %s;:VOLT:UNIT VPP;*OPC?;' % str(vpp))

    def afg_set_function_shape(self, ch=1, function_shape=0):
        shape_list = {
            0: "SIN",
            1: "RAMP",
            2: "SQUARE",
        }
        return self.inst.query(':FUNC:SHAP %s;*OPC?;' % shape_list.get(function_shape, "SIN"))

    def afg_set_frequency(self, ch=1, frequency=1000):
        return self.inst.query(':FREQ %s;*OPC?;' % str(frequency))

    def reset_instrument(self):
        return self.inst.query('*RST;*OPC?')

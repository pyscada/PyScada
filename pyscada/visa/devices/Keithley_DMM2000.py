# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.visa.devices import GenericDevice
from pyscada.models import VariableProperty
import re
import logging
logger = logging.getLogger(__name__)
import time


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
        vp_func = variable_instance.variableproperty_set.filter(name=':FUNC').first()
        measure_function = ''
        if vp_func:
            if vp_func.value():
                measure_function = ':FUNC "%s";'%vp_func.value()

        trig_delay = 0.1
        if variable_instance.visavariable.device_property.upper() == 'PRESENT_VALUE':
            return self.parse_value(self.inst.query(':FETCH?'))
        m = re.search('(PRESENT_VALUE_CH)([0-9]*)', variable_instance.visavariable.device_property.upper())
        if m:
            return self.parse_value(
                        self.inst.query(':route:close (@%s);%s:TRIG:DEL %1.3f;:fetch?'%(m.group(2),measure_function,trig_delay)))
        return self.parse_value(self.inst.query(variable_instance.visavariable.device_property.upper()))

    def write_data(self, variable_id, value, task):
        """
        write values to the device
        """
        variable = self._variables[variable_id]
        if task.property_name != '':
            # write the property to VariableProperty use that for later read
            vp = VariableProperty.objects.update_or_create_property(variable=variable,
                                                                    name='VISA:%s' % task.property_name.upper(),
                                                                    value=value, value_class='FLOAT64')
            return True
        return False
        i = 0
        j = 0
        while i < 10:
            try:
                self.inst.read_termination = '\n'
                self.inst.query('*IDN?')
                i = 12
                j = 1
            except:
                self.connect()
                time.sleep(1)
                i += 1
                logger.error("Keithley connect error i : %s" %i)
        if j == 0:
            logger.error("Keithley-Instrument not connected")
            return False

        # if variable_id == 'present_value':
        if task.variable.visavariable.device_property.upper() == 'PRESENT_VALUE':
            i = 0
            while i < 10:
                Vseff = ""
                try:
                    Vseff = self.parse_value(self.inst.query(':READ?'))
                except:
                    Vseff = ""
                if Vseff is None or Vseff is "":
                    i += 1
                    logger.error("Keithley - Error Read - i : %s" %i)
                    self.inst.write('*CLS')
                else:
                    i = 12
                    # Call Phase Osc
                    # cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='Find_Phase_Osc').id, value=Vseff, start=time.time())
                    # cwt.save()
                    logger.info("Variable %s - task.property_name : %s - value %s" %(variable, task.property_name.upper(), value))
                    vp = VariableProperty.objects.update_or_create_property(variable=variable,
                                                                   name='VISA:%s' % task.property_name.upper(),
                                                                   value=value, value_class='FLOAT64')
                    #vp = VariableProperty.objects.update_or_create_property(variable=variable,
                    #                                               name='VISA:%s' % task.property_name.upper())
            return Vseff

        if variable_instance.visavariable.device_property.upper() == 'SET_AC_RANGE_RES':
        # if variable_id == 'set_ac_range_res':
            CMD = str('*RST;:FUNC "VOLTage:AC";:VOLTage:AC:RANGe:AUTO 1;:VOLTage:AC:RESolution MIN;:TRIG:DEL MIN')
            self.inst.write(CMD)
            return True
        else:
            logger.error("Keithley - variable_id : %s" %variable_id)
            return self.parse_value(self.inst.query(str(variable_id)+' '+str(value)))

    def parse_value(self, value):
        """
        takes a string in the Keithley DMM 2000 format and returns a float value or None if not parse able
        """
        try:
            return float(value)
        except:
            return None

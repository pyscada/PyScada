# -*- coding: utf-8 -*-
import sys

try:
    import visa
    driver_visa_ok = True
except ImportError:
    driver_visa_ok = False

from time import time


class Device:
    def __init__(self,device):
        self.variables = []
        self.device = device
        if self.device.visadevice.instrument.handler_path is not None:
            sys.path.append(self.device.visadevice.instrument.handler_path)
        try:
            mod = __import__(self.device.visadevice.instrument.handler_class, fromlist=['Handler'])
            DeviceHandler = getattr(mod, 'Handler')
            self._h = DeviceHandler(self.device)
            driver_handler_ok = True
        except ImportError:
            driver_handler_ok = False
            
        for var in self.device.variable_set.filter(active=1):
            if not hasattr(var,'visavariable'):
                continue
            self.variables.append(var)
        
        if driver_visa_ok and driver_handler_ok:
            self._h.connect()

    def request_data(self):
        """
        request data from the instrument/device
        """
        output = []
        if not driver_visa_ok:
            return output
        
        for item in self.variables:
            if not item.visavariable.variable_type == 1:
                # skip all config values
                continue
            
            value = self._h.read_data(item.visavariable.device_property)
            
            if value is not None and item.update_value(value,time()):
                output.append(item.create_recorded_data_element())
        
        return output
    
    

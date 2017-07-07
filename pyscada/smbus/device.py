# -*- coding: utf-8 -*-

try:
    import smbus
    driver_ok = True
except ImportError:
    driver_ok = False
    

from time import time


class Device:
    def __init__(self,device):
        self.variables = []
        self.device = device
        self.i2c = None
        for var in device.variable_set.filter(active=1):
            if not hasattr(var,'smbusvariable'):
                continue
            self.variables.append(var)

    def connect(self):
        """

        """
        self.i2c = smbus.SMBus(int(self.device.smbusdevice.port))

    def request_data(self):
        """
        
        """
        if not driver_ok:
            return None
        self.connect()
        output = []
        for item in self.variables:
            if self.device.smbusdevice.device_type == 'ups_pico':
                from pyscada.smbus.device_templates.ups_pico import ups_pico
                value = ups_pico(self.i2c,item.smbusvariable.information)
                
            else:
                value = None
            # update variable
            if value is not None:
                if item.update_value(value,time()):
                    output.append(item.create_recorded_data_element())

        return output
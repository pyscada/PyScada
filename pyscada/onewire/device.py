# -*- coding: utf-8 -*-
from pyscada.models import Device

try:
    #import psutil
    import sys, os
    driver_ok = True
except ImportError:
    driver_ok = False
    

from time import time

class Device:
    def __init__(self,device):
        self.variables  = []
        self.device = device
        for var in device.variable_set.filter(active=1):
            if not hasattr(var,'onewirevariable'):
                continue
            self.variables.append(var)
            
    def request_data(self):
        '''
        
        '''
        if not driver_ok:
            return None
        #todo add support for OWFS?
        # read in a list of known devices from w1 master
        file = open('/sys/devices/w1_bus_master1/w1_master_slaves')
        w1_slaves_raw = file.readlines()
        file.close()
        # extract all 1wire addresses
        w1_slaves = []
        for line in w1_slaves_raw:
            # extract 1-wire addresses
            w1_slaves.append(line.split("\n")[0][3::])
        
        output = []
        for item in self.variables:
            timestamp = time()
            value = None
            if item.onewirevariable.address.lower() in w1_slaves:
                file = open('/sys/bus/w1/devices/' + str('28-' + item.onewirevariable.address) + '/w1_slave')
                filecontent = file.read()
                file.close()
                if item.onewirevariable.sensor_type in ['DS18B20']:
                    # read and convert temperature
                    if filecontent.split('\n')[0].split('crc=')[1][3::] == 'YES':
                        value = float(filecontent.split('\n')[1].split('t=')[1]) / 1000
            # update variable
            if value is not None and item.update_value(value,timestamp):
                output.append(item.create_recorded_data_element())
            
            
        return output
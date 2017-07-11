# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from time import time
driver_ok = True
try:
    import pyownet

    driver_owserver_ok = True
except ImportError:
    driver_owserver_ok = False


class Device:
    def __init__(self, device):
        self.variables = []
        self.device = device
        for var in device.variable_set.filter(active=1):
            if not hasattr(var, 'onewirevariable'):
                continue
            self.variables.append(var)

    def request_data(self):
        """

        """
        if self.device.onewiredevice.adapter_type == 'rpi_gpio4':
            # RPi GPIO 4
            if not driver_ok:
                return None
            # read in a list of known devices from w1 master
            f = open('/sys/devices/w1_bus_master1/w1_master_slaves')
            w1_slaves_raw = f.readlines()
            f.close()
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
                    f = open('/sys/bus/w1/devices/' + str('28-' + item.onewirevariable.address) + '/w1_slave')
                    filecontent = f.read()
                    f.close()
                    if item.onewirevariable.sensor_type in ['DS18B20']:
                        # read and convert temperature
                        if filecontent.split('\n')[0].split('crc=')[1][3::] == 'YES':
                            value = float(filecontent.split('\n')[1].split('t=')[1]) / 1000
                # update variable
                if value is not None and item.update_value(value, timestamp):
                    output.append(item.create_recorded_data_element())
            return output
        # OWServer
        elif self.device.onewiredevice.adapter_type == 'owserver':
            if not driver_owserver_ok:
                return None
            hostname = 'localhost'
            port = 4304
            if self.device.onewiredevice.config != '':
                hostname = self.device.onewiredevice.config.split(':')
                if len(hostname) > 1:
                    port = hostname[1]
                hostname = hostname[0]

            try:
                owproxy = pyownet.protocol.proxy(host=hostname, port=port, flags=pyownet.protocol.FLG_UNCACHED)
            except:
                return None
            w1_slaves = []
            for item in owproxy.dir():
                w1_slaves.append(item.lower())

            output = []
            for item in self.variables:
                timestamp = time()
                value = None
                if item.onewirevariable.sensor_type in ['DS18B20']:
                    if '/28.%s/' % item.onewirevariable.address.lower() in w1_slaves:
                        # read and convert temperature
                        try:
                            value = float(owproxy.read('/28.%s/temperature' % item.onewirevariable.address))
                        except:
                            value = None

                # update variable
                if value is not None and item.update_value(value, timestamp):
                    output.append(item.create_recorded_data_element())
            return output

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.visa.devices import GenericDevice
from pyscada.models import VariableProperty
from datetime import datetime
from math import floor

import logging

logger = logging.getLogger(__name__)
# -*- coding: utf-8 -*-
"""Object based access to the PI C-633 Stepper Motor Controller


Example::

    unit = C633('ASRL/dev/ttyUSB0::INSTR')
    unit.connect()
    unit.disconnect()
"""
__author__ = "Martin Schröder"
__copyright__ = "Copyright 2019, Technische Universität Berlin"
__credits__ = []
__license__ = "GPLv3"
__version__ = "0.1.0"
__maintainer__ = "Martin Schröder"
__email__ = "m.schroeder@tu-berlin.de"
__status__ = "Beta"
__docformat__ = 'reStructuredText'

import pyvisa
from datetime import datetime
from math import floor
from time import sleep, time


class C633(object):
    _isconfigured = False
    pos_max = -1
    pos_min = -1
    
    def __init__(self):
        self.instr = None

    def connect(self, instr):
        if self.instr is None and instr is None:
            return
        self.instr = instr
    
    def configure(self):
        logger.debug(self.instr.query('*IDN?'))
        logger.debug(self.instr.query('ERR?'))
        self.instr.write('SVO 1 1')  # enable servo 1
        logger.debug(self.instr.query('SVO?'))
        logger.debug(self.instr.query('POS?'))
        self.instr.write('FNL 1')  # reference move to lower limit
        timeout = time() + 10 # 10s timeout
        while self.instr.query('FRF?') != '1=1':
            sleep(0.1)
            logger.debug(self.instr.query('POS?'))
            if time() > timeout:
                return False
        self.pos_max = self.parse_value(self.instr.query('TMX?'))
        self.pos_min = self.parse_value(self.instr.query('TMN?'))
        self._isconfigured = True

    def get_value(self,stage=1):
        pos_data = self.instr.query('POS?')
        return self.parse_value(pos_data, stage=stage)
    
    def set_value(self,pos,stage=1):
        if not self._isconfigured:
            return False
        if pos > self.pos_max:
            return False
        if pos < self.pos_min:
            return False
        self.instr.write('MOV %d %1.8f'%(stage,pos))
    
    def parse_value(self,str_data,stage=1, **kwargs):
        data = str_data.split('=')
        return float(data[-1])
    
    def query(self,cmd):
        self.instr.timeout = 1000
        self.instr.write(cmd)
        data = []
        while True: 
            d = self.instr.read()
            if d == '':
                break
            data.append(d)
        return data

from time import sleep
class Handler(GenericDevice):
    """
    C-633 and other Devices with the same command set
    """
    smc = None
    def connect(self):
        #super(Handler, self).connect()
        super().connect()
        self.smc = C633()
        if self.inst is None:
            return
        try:
            logger.info(self.inst.query('*IDN?'))
        except:
            self.inst = None
            return
        self.smc.connect(self.inst)
        #for variable in self._variables.values():
        #    data_type, channel = variable.visavariable.device_property.upper().split(';')
        #    self.smc.set_channel(channel=channel, data_type=data_type)
        self.smc.configure()

    def before_read(self):
        pass

    def read_data(self,variable_instance):
        """
        read values from the device
        """
        if self.inst is None:
            return None
        if not self.smc._isconfigured:
            return None
        stage = int(variable_instance.visavariable.device_property.upper())
        return self.smc.get_value(stage)


    def write_data(self,variable_id, value, task):
        """
        write values to the device
        """
        variable = self._variables[variable_id]
        if task.variable_property is not None:
            # write the freq property to VariableProperty use that for later read
            vp = VariableProperty.objects.update_or_create_property(variable=variable, name=task.property_name.upper(),
                                                        value=value, value_class='FLOAT64')
            return True
        if variable.visavariable.variable_type == 0:  # configuration
            # only write to configuration variables
            stage = int(variable.visavariable.device_property.upper())
            self.smc.set_value(value,stage)
            return value
        else:
            return False

    def parse_value(self,result, **kwargs):
        """
        takes a string in the HP3456A format and returns a float value or None if not parseable
        """
        try:
            i = 0
            value = result[i]
            """
            timestamp = datetime(int(result[i+1]),
                                 int(result[i+2]),
                                 int(result[i+3]),
                                 int(result[i+4]),
                                 int(result[i+5]),
                                 int(floor(result[i+6])),
                                 int(round((result[i+6]%1)*1000))).timestamp()
            """
            return value
        except:
            return None


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.visa.devices import GenericDevice
from pyscada.models import VariableProperty
from datetime import datetime
from math import floor

import logging

logger = logging.getLogger(__name__)
# -*- coding: utf-8 -*-
"""Object based access to the HP34970A, Agilent 34970A/34972A , Keysight 34970A Data Acquisition / switching unit


Example::

    from HP34970A import HP34970A, Channel, DataTypes
    unit = HP34970A('ASRL/dev/ttyUSB0::INSTR')
    unit.connect()
    unit.set_channel(1,1,DataType.TEMP_RTD_85)  # set channel 1 on bank 1 to Temperature 2-Wire RTD and  a = 0.00385
    unit.set_channel(1,2,DataType.TEMP_FRTD_85) # set channel 2 on bank 1 to Temperature 4-Wire RTD and  a = 0.00385
    unit.set_channel(1,3,DataType.TEMP_TC_T)  # set channel 3 on bank 1 to Temperature Thermocouple Typ T
    timestamp, value = instr.get_value(1,1)  # read measurement from channel 1 on bank 1
    if value:
        print('CH1: %1.3f'%value)
    instr.scan_all()  # scan all configured channels and write to internal (object) memory
    timestamp, value = instr.get_mvalue(1,1)  # read internal (object) memory of channel 1 on bank 1
    if value:
        print('CH1: %1.3f'%value)
    unit.disconnect()
"""
__author__ = "Martin Schröder"
__copyright__ = "Copyright 2018, Technische Universität Berlin"
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
from time import sleep

class DataType(object):
    CURRENT_AC = 'CURR:AC'
    CURRENT_DC = 'CURR:DC'
    CURRENT_DC_10mA = 'CURR:DC 10mA'
    CURRENT_DC_100mA = 'CURR:DC 100mA'
    CURRENT_DC_1A = 'CURR:DC 1A'
    CURRENT_AC_10mA = 'CURR:AC 10mA'
    CURRENT_AC_100mA = 'CURR:AC 100mA'
    CURRENT_AC_1A = 'CURR:AC 1A'
    FREQUENCY = 'FREQ'
    PERIOD = 'PER'
    RESISTANCE = 'RES'  # 2-Wire Resistance
    RESISTANCE_100ohm = 'RES 100W'  # 2-Wire Resistance
    RESISTANCE_1kohm = 'RES 1kW'  # 2-Wire Resistance
    RESISTANCE_10kohm = 'RES 10kW'  # 2-Wire Resistance
    RESISTANCE_100kohm = 'RES 100kW'  # 2-Wire Resistance
    RESISTANCE_1Mohm = 'RES 1MW'  # 2-Wire Resistance
    RESISTANCE_10Mohm = 'RES 10MW'  # 2-Wire Resistance
    RESISTANCE_100Mohm = 'RES 100MW'  # 2-Wire Resistance
    FRESISTANCE = 'FRES'  # 4-Wire Resistance
    FRESISTANCE_100ohm = 'FRES 100W'  # 4-Wire Resistance
    FRESISTANCE_1kohm = 'FRES 1kW'  # 4-Wire Resistance
    FRESISTANCE_10kohm = 'FRES 10kW'  # 4-Wire Resistance
    FRESISTANCE_100kohm = 'FRES 100kW'  # 4-Wire Resistance
    FRESISTANCE_1Mohm = 'FRES 1MW'  # 4-Wire Resistance
    FRESISTANCE_10Mohm = 'FRES 10MW'  # 4-Wire Resistance
    FRESISTANCE_100Mohm = 'FRES 100MW'  # 4-Wire Resistance
    TEMPERATURE = 'TEMP'
    TEMP_TC_B = 'TEMP TC,B'
    TEMP_TC_E = 'TEMP TC,E'
    TEMP_TC_J = 'TEMP TC,J'
    TEMP_TC_K = 'TEMP TC,K'
    TEMP_TC_N = 'TEMP TC,N'
    TEMP_TC_R = 'TEMP TC,R'
    TEMP_TC_S = 'TEMP TC,S'
    TEMP_TC_T = 'TEMP TC,T'
    TEMP_RTD_85 = 'TEMP RTD,85'
    TEMP_RTD_91 = 'TEMP RTD,85'
    TEMP_FRTD_85 = 'TEMP FRTD,85'
    TEMP_FRTD_91 = 'TEMP FRTD,85'
    TEMP_TERM_2252 = 'TEMP TERM,2252'
    TEMP_TERM_5000 = 'TEMP TERM,5000'
    TEMP_TERM_10000 = 'TEMP TERM,10000'
    TOTALIZE='TOT'
    VOLTAGE_AC='VOLT:AC'
    VOLTAGE_DC = 'VOLT:DC'
    VOLTAGE_AC_100mV = '100mV'
    VOLTAGE_AC_1V = 'VOLT:AC 1V'
    VOLTAGE_AC_10V = 'VOLT:AC 10V'
    VOLTAGE_AC_100V = 'VOLT:AC 100V'
    VOLTAGE_AC_300V = 'VOLT:AC 300V'
    VOLTAGE_DC_100mV = 'VOLT:DC 100mV'
    VOLTAGE_DC_1V = 'VOLT:DC 1V'
    VOLTAGE_DC_10V = 'VOLT:DC 10V'
    VOLTAGE_DC_100V = 'VOLT:DC 100V'
    VOLTAGE_DC_300V = 'VOLT:DC 300V'


class Channel(object):
    data_type = DataType.VOLTAGE_DC
    value = None
    timestamp = None

    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

BANKS = [1, 2, 3]
CHANNELS = range(1,21)

class HP34970A(object):

    banks = None
    _isconfigured = False
    def __init__(self):
        self.instr = None
        self._queries = dict()
        self._channels = dict()
        self.banks = []

    def connect(self, instr):
        if self.instr is None and instr is None:
            return
        self.instr = instr
        self.instr.write("STATus:PRESet")
        self.instr.write('SYST:TIME %s'%(datetime.now().strftime("%H,%M,%S.000")))  # set unit time
        self.instr.write('SYST:DATE %s'%(datetime.now().strftime("%Y,%m,%d")))  # set unit date
        self.instr.write('FORM:READ:TIME:TYPE ABS')
        dispstring = "Booting."
        for i in range(len(dispstring)-13):
            self.instr.write('DISP:TEXT "%s"'%dispstring[i:i+13], encoding="ascii")
            sleep(0.1)
        self.instr.write('DISP:TEXT "Done"', encoding="ascii")
        sleep(1)
        self.instr.write('DISP:TEXT:CLE')
        for bank in BANKS:
            card_type = self.instr.query("SYSTem:CTYPe? %d00"%bank)
            if card_type in  ["HEWLETT-PACKARD,34901A,0,2.3"]:
                self.banks.append(bank)

    def set_channel(self, channel='101', data_type=DataType.VOLTAGE_DC, **kwargs):
        self._channels[channel] = Channel(data_type=data_type)
        self._isconfigured = False

    def configure(self):
        self._queries = dict()
        for channel_nr, channel in self._channels.items():
            if channel.data_type not in self._queries:
                self._queries[channel.data_type] = '(@%s'%channel_nr
            else:
                self._queries[channel.data_type] += ',%s'%channel_nr

        for data_type in self._queries.keys():
            self.instr.write('CONF:%s,%s)'%(data_type, self._queries[data_type]))
        self._isconfigured = True

    def scan_all(self):
        if not self._isconfigured:
            return
        for data_type in self._queries.keys():
            self.scan(data_type)

    def scan(self,data_type):
        for bank in self.banks:
            self.instr.write('ROUT:CHAN:DEL:AUTO ON,(@%d01:%d20)'%(bank,bank))
        #self.instr.write('CONF:%s,%s)'%(data_type, self._queries[data_type]))
        self.instr.write('FORM:READ:TIME:TYPE ABS')
        self.instr.write('FORM:READ:TIME ON')
        self.instr.write('FORM:READ:CHAN ON')
        self.instr.write('ROUT:SCAN %s)'%self._queries[data_type])
        self.instr.write('INIT')
        self.instr.write('FETC?')
        result = self.instr.read_ascii_values()
        self._parse_result(result)

    def get_value(self,bank,channel_nr):
        channel = self._get_ch_str(bank, channel_nr)
        data_type = self._channels[channel].data_type
        #self.instr.write('CONF:%s,(@%s)'%(data_type,channel))
        self.instr.write('FORM:READ:TIME:TYPE ABS')
        self.instr.write('FORM:READ:TIME ON')
        self.instr.write('FORM:READ:CHAN ON')
        self.instr.write('ROUT:SCAN (@%s)'%channel)
        self.instr.write('INIT')
        self.instr.write('FETC?')
        result = self.instr.read_ascii_values()
        self._parse_result(result)
        return self.get_mvalue(bank, channel_nr)

    def get_mvalue(self,bank,channel_nr):
        """reads the value of channel from the object memory (self._channels)

        :param bank: number of the bank [1:3]
        :param channel_nr: number of the channel [1:20]
        :return: [timestamp, value]
        """
        channel = self._get_ch_str(bank,channel_nr)
        return self._channels[channel].timestamp, self._channels[channel].value

    @staticmethod
    def _get_ch_str(bank,channel_nr):
        if channel_nr not in CHANNELS:
            raise ValueError('Channel out of range %r' % CHANNELS)
        if bank not in BANKS:
            raise ValueError('Bank out of range %r' % BANKS)

        return '%d%02.2G' % (bank, channel_nr)

    def _parse_result(self,result):
        for i in range(0,len(result),8):
            channel = str(int(result[i+7]))  # Channel number
            self._channels[channel].value = result[i]
            self._channels[channel].timestamp = datetime(int(result[i+1]),
                                                         int(result[i+2]),
                                                         int(result[i+3]),
                                                         int(result[i+4]),
                                                         int(result[i+5]),
                                                         int(floor(result[i+6])),
                                                         int(round((result[i+6]%1)*1000))).timestamp()

from time import sleep
class Handler(GenericDevice):
    """
    HP34970A and other Devices with the same command set
    """
    dmm = None
    def connect(self):
        super(Handler, self).connect()
        self.dmm = HP34970A()
        if self.inst is None:
            return
        try:
            logger.info(self.inst.query('*IDN?'))
        except:
            self.inst = None
            return
        self.dmm.connect(self.inst)
        for variable in self._variables.values():
            data_type, channel = variable.visavariable.device_property.upper().split(';')
            self.dmm.set_channel(channel=channel, data_type=data_type)
        self.dmm.configure()

    def before_read(self):
        self.dmm.scan_all()

    def read_data_and_time(self,variable_instance):
        """
        read values from the device
        """
        if self.inst is None:
            return None, None
        data_type, channel = variable_instance.visavariable.device_property.upper().split(';')
        return self.dmm._channels[channel].value, self.dmm._channels[channel].timestamp

    def write_data(self,variable_id, value, task):
        """
        write values to the device
        """
        return super().write_data(variable_id, value, task)

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


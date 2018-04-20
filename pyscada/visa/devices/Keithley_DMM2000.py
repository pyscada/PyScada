# -*- coding: utf-8 -*-
from pyscada.visa.devices import GenericDevice
from pyscada.models import DeviceWriteTask, Variable, Device
from pyscada.models import RecordedData
import time
import math

import logging

logger = logging.getLogger(__name__)

class Handler(GenericDevice):
    '''
    HP3456A and other Devices with the same command set
    '''

    def read_data(self,device_property):
        '''
        read values from the device
        '''
        if self.inst is None:
            logger.error("Visa-Keithley-read data-Self.inst : None")
            return None
        if device_property == 'present_value':
            logger.info("Keithley READ Handler")
            return self.parse_value(self.inst.query(':READ?'))
        else:
            value = self.inst.query(device_property)
            logger.info("Visa-Keithley-read data-property : %s - value : %s" %(device_property, value))
            return self.parse_value(value)
        return None

    def write_data(self,variable_id, value):
        '''
        write values to the device
        '''
        i=0
        j=0
        while i<10:
            try:
                self.inst.query('*IDN?')
                #logger.info("Visa-Keithley-Write- variable_id : %s et value : %s" %(variable_id, value))
                i=12
                j=1
            except:
                time.sleep(1)
                i += 1
                logger.error("Keithley connect error i : %s" %i)
        if j == 0:
            logger.error("Keithley-Instrument non connecté")
            return False
        if variable_id == 'present_value':
            i = 0
            while i<10:
                T1=time.time()
#                self.inst.timeout(5)
#                res=self.inst.timeout
#                logger.info("timeout : %s" %res)
#                self.inst.write(':READ?')
#                time.sleep(0.1)
#                Vseff = self.parse_value(self.inst.read(termination='\n'))
#                Vseff = self.parse_value(self.inst.read())
                self.inst.read_termination = '\n'
                Vseff = ""
                try:
                    Vseff = self.parse_value(self.inst.query(':READ?'))
                    T2=time.time()
                except:
                    Vsedd = ""
                if Vseff is None or Vseff is "":
                    i += 1
                    logger.error("Keithley - Error Read - i : %s" %i)
                    self.inst.write('*CLS')
                else:
                    i = 12
                    #Call Phase Osc
                    T3=time.time()
                    cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='Find_Phase_Osc').id, value=Vseff, start=time.time())
                    cwt.save()
                    T4=time.time()
#            logger.info("Read time - query : %s - vide : %s - save db : %s" %(T2-T1, T3-T2, T4-T3))
            return Vseff
        if variable_id == 'set_ac_range_res':
#            Veeff = float(value)/float(math.sqrt(2))
            self.inst.read_termination = '\n'
            CMD = str('*RST;:FUNC "VOLTage:AC";:VOLTage:AC:RANGe:AUTO 1;:VOLTage:AC:RESolution MIN;:TRIG:DEL MIN')
            self.inst.write(CMD)
            return True
        else:
            return self.parse_value(self.inst.query(str(variable_id)+' '+str(value)))


    def parse_value(self,value):
        '''
        takes a string in the HP3456A format and returns a float value or None if not parseable
        '''
        try:
            return float(value)
        except:
            return None


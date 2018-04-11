# -*- coding: utf-8 -*-
from pyscada.visa.devices import GenericDevice
from pyscada.models import DeviceWriteTask, Variable, Device
from pyscada.models import RecordedData
import time

import logging

logger = logging.getLogger(__name__)

class Handler(GenericDevice):
    '''
    Tektronix AFG1022 and other Devices with the same command set
    '''

    def read_data(self,device_property):
        '''
        read values from the device
        '''
        if self.inst is None:
            logger.error("Visa-AFG1022-read data-Self.inst : None")
            return None
        if device_property == 'present_value':
            return self.parse_value(self.inst.query(':READ?'))
        else:
            value = self.inst.query(device_property)
            logger.info("Visa-AFG1022-read data-property : %s - value : %s" %(device_property, value))
#            return value.split(',')[0]
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
                #self.inst.query('*IDN?')
                #logger.info("Visa-AFG1022-Write-variable_id : %s et value : %s" %(variable_id, value))
                i=12
                j=1
            except:
                time.sleep(1)
                i += 1
                logger.error("AFG1022 connect error i : %s" %i)
        if j == 0:
            logger.error("AFG1022-Inst NOT connected")
            return None
        if variable_id == 'init_BODE':
            
            #N
            try:
                N = int(RecordedData.objects.last_element(variable_id=16).value())
            except:
                N = 0
                #logger.error('AFG1022 cannot load N')
            if N == 0:
                #Set N to 1
                cwt = DeviceWriteTask(variable_id=16, value=1, start=time.time())
                cwt.save()
                #ReCall init GBF
                cwt = DeviceWriteTask(variable_id=3, value=1, start=time.time())
                cwt.save()
                return None
            elif N == 1:
                #Récup de Ve
                Vepp = RecordedData.objects.last_element(variable_id=11)
                #Fmin
                Fmin = RecordedData.objects.last_element(variable_id=12)
                #Call Range MM
                cwt = DeviceWriteTask(variable_id=1, value=Vepp.value(), start=time.time())
                cwt.save()
                #Call Init Osc
                cwt = DeviceWriteTask(variable_id=6, value=1, start=time.time())
                cwt.save()
                #Reset GBF
                CMD = str('*RST;OUTPut1:STATe ON;OUTP1:IMP MAX;SOUR1:AM:STAT OFF;SOUR1:FUNC:SHAP SIN;SOUR1:VOLT:LEV:IMM:AMPL '+str(Vepp.value())+'Vpp')
                self.inst.write(CMD)
#                self.inst.write('*CLS')
                #Set F value
                cwt = DeviceWriteTask(variable_id=15, value=Fmin.value(), start=time.time())
                cwt.save()
                #Call  Set Freq GBF
#                cwt = DeviceWriteTask(variable_id=7, value=Fmin.value(), start=time.time())
#                cwt.save()
                self.write_data("set_freq", Fmin.value())
                return True
            else:
                cwt = DeviceWriteTask(variable_id=3, value=1, start=time.time())
                cwt.save()
                logger.info("Init GBF - N : %s" %N)
                return False
            return None
        elif variable_id == 'set_freq':
            #Define Freq
            self.inst.write('SOUR1:FREQ:FIX '+str(value))
            #Call Read MM
            cwt = DeviceWriteTask(variable_id=2, value=1, start=time.time())
            cwt.save()
            return self.parse_value(value)
        elif variable_id == 'set_tension':
            #Define tension
            self.inst.write('SOUR1:VOLT:LEV:IMM:AMPL '+str(value)+'Vpp')
            #F = Fmin
            F = RecordedData.objects.last_element(variable_id=12)
            #Set F value
            cwt = DeviceWriteTask(variable_id=15, value=F.value(), start=time.time())
            cwt.save()
            #Call  Set Freq GBF
            cwt = DeviceWriteTask(variable_id=7, value=F.value(), start=time.time())
            cwt.save()
            return self.parse_value(value)
        elif variable_id == 'return_value':
            return self.parse_value(value)
        else:
            return self.parse_value(self.inst.query(str(variable_id)+' '+str(value)))
        return None

    def parse_value(self,value):
        '''
        takes a string in the HP3456A format and returns a float value or None if not parseable
        '''
        try:
            return float(value)
        except:
            return None

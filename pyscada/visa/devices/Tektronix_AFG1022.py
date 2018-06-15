# -*- coding: utf-8 -*-
from pyscada.visa.devices import GenericDevice
from pyscada.models import DeviceWriteTask, Variable, Device
from pyscada.models import RecordedData
import time

import logging

logger = logging.getLogger(__name__)

class Handler(GenericDevice):
    """
    Tektronix AFG1022 and other Devices with the same command set
    """

    def read_data(self,device_property):
        """
        read values from the device
        """
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
        """
        write values to the device
        """
        i=0
        j=0
        while i<10:
            try:
                self.inst.query('*IDN?')
                #logger.info("Visa-AFG1022-Write-variable_id : %s et value : %s" %(variable_id, value))
                i=12
                j=1
            except:
                self.connect()
                time.sleep(1)
                i += 1
                logger.error("AFG1022 connect error i : %s" %i)
        if j == 0:
            logger.error("AFG1022-Instrument non connecté")
            return None
        if variable_id == 'init_BODE':

            #N
            try:
                N = int(RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_n').id).value())
            except:
                N = 0
                logger.error('AFG1022 cannot load N')
            if N == 0:
                #Set N to 1
                cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='BODE_n').id, value=1, start=time.time())
                cwt.save()
                #ReCall init GBF
                cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='Init_BODE_GBF').id, value=1, start=time.time())
                cwt.save()
                return None
            elif N == 1:
                self.inst.read_termination = '\n'
                #Récup de Ve
                Vepp = RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_Vpp').id).value()
                #Fmin
                Fmin = RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_Fmin').id).value()
                #Call Range MM
                cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='Set_AC_Range_and_Resolution_and_Measure_MM').id, value=Vepp, start=time.time())
                cwt.save()
                #Call Init Osc
                cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='Init_BODE_Osc').id, value=1, start=time.time())
                cwt.save()
                #Reset GBF
                CMD = str('*RST;OUTPut1:STATe ON;OUTP1:IMP MAX;SOUR1:AM:STAT OFF;SOUR1:FUNC:SHAP SIN;SOUR1:VOLT:LEV:IMM:AMPL '+str(Vepp)+'Vpp')
                self.inst.write(CMD)
#                self.inst.write('*CLS')
                #Set F value
                cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='BODE_F').id, value=Fmin, start=time.time())
                cwt.save()
                #Call  Set Freq GBF
#                cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='Set_Freq_GBF').id, value=Fmin, start=time.time())
#                cwt.save()
                self.write_data("set_freq", Fmin)
                return True
            else:
                cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='Init_BODE_GBF').id, value=1, start=time.time())
                cwt.save()
                logger.info("Init GBF - N : %s" %N)
                return False
            return None
        elif variable_id == 'set_freq':
            #Define Freq
            self.inst.write('SOUR1:FREQ:FIX '+str(value))
            #Call Read MM
            cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='Read_MM_acual_value').id, value=1, start=time.time())
            cwt.save()
            return self.parse_value(value)
        elif variable_id == 'set_tension':
            #Define tension
            self.inst.write('SOUR1:VOLT:LEV:IMM:AMPL '+str(value)+'Vpp')
            #F = Fmin
            F = RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_Fmin').id).value()
            #Set F value
            cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='BODE_F').id, value=F, start=time.time())
            cwt.save()
            #Call  Set Freq GBF
            cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='Set_Freq_GBF').id, value=F, start=time.time())
            cwt.save()
            return self.parse_value(value)
        elif variable_id == 'return_value':
            return self.parse_value(value)
        elif variable_id == 'reboot':
            import os
            os.system('sudo reboot')
            return 1
        else:
            return self.parse_value(self.inst.query(str(variable_id)+' '+str(value)))
        return None

    def parse_value(self,value):
        """
        takes a string in the Tektronix AFG1022 format and returns a float value or None if not parseable
        """
        try:
            return float(value)
        except:
            return None

# -*- coding: utf-8 -*-
from pyscada.visa.devices import GenericDevice
from pyscada.models import DeviceWriteTask, Variable, Device
from pyscada.models import RecordedData
import time
import math
from math import log10, exp

import logging
logger = logging.getLogger(__name__)

try:
    import numpy as np
except:
    logger.error("Need to install numpy : pip install numpy")

class Handler(GenericDevice):
    """
    Tektronix MDO3014 and other Devices with the same command set
    """

    def read_data(self, device_property):
        """
        read values from the device
        """
        if self.inst is None:
            logger.error("Visa-MDO3014-read data-Self.inst : None")
            return None
        if device_property == 'present_value':
            return self.parse_value(self.inst.query(':READ?'))
        else:
            value = self.inst.query(device_property)
            logger.info("Visa-MDO3014-read data-property : %s - value : %s" %(device_property, value))
            return self.parse_value(value)
        return None

    def write_data(self, variable_id, value):
        """
        write values to the device
        """
        i = 0
        j = 0
        while i < 10:
            try:
                self.inst.query('*IDN?')
                # logger.info("Visa-MDO3014-Write- variable_id : %s et value : %s" %(variable_id, value))
                i = 12
                j = 1
            except:
                self.connect()
                time.sleep(1)
                i += 1
                logger.error("MDO3014 connect error i : %s" % i)
        if j == 0:
            logger.error("MDO3014-Instrument not connected")
            return None
        if variable_id == 'init_BODE':
            self.inst.read_termination = '\n'
            # Reset and init Osc
            Vepp = RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_Vpp').id)
            # self.inst.write('*CLS')
            self.inst.write('*RST;:SEL:CH1 1;:SEL:CH2 1;:HORIZONTAL:POSITION 0;:CH1:YUN "V";:CH1:SCALE '
                            + str(1.2*float(Vepp.value())/(2*4))+';:CH2:YUN "V";:CH2:BANdwidth 10000000;:'
                                                                 'CH1:BANdwidth 10000000;:TRIG:A:TYP EDGE;'
                                                                 ':TRIG:A:EDGE:COUPLING DC;:TRIG:A:EDGE:SOU CH1;'
                                                                 ':TRIG:A:EDGE:SLO FALL;:TRIG:A:MODE NORM')
            return True
        elif variable_id == 'find_phase':
            # N = int(RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_n').id).value())
            # if N == 1:
            #     time.sleep(1)
            i = 0
            F = RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_F').id)
            while F is None and i<10:
                F = RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_F').id)
                i += 1
            Vsff = value
            Vsmax = float(Vsff)*float(math.sqrt(2))
            CMD = str(':HORIZONTAL:SCALE '+str(round(float(float(4)/(float(10)*float(F.value()))),6))+';:CH2:SCALE '
                      +str(1.4*float(Vsmax)/4)+';:TRIG:A:LEV:CH1 '+str(0.8*float(Vsmax)) +
                      ';:MEASUrement:IMMed:SOUrce1 CH1;:MEASUrement:IMMed:SOUrce2 CH2;:MEASUREMENT:IMMED:TYPE PHASE')
            self.inst.write(CMD)
            time.sleep(20/F.value())
            CMD = str(':MEASUREMENT:IMMED:VALUE?')
            Phase = []
            for k in range(1, 4):
                Phase.append(float(self.inst.query(CMD)))
                time.sleep(0.1)
            MeanPhase = np.mean(Phase)
            StDevPhase = np.std(Phase)
            logger.info("Phase : %s - Mean : %s - StDev : %s" %(Phase, MeanPhase, StDevPhase))
            i=0
            while (float(MeanPhase) > 100000 or StDevPhase > 3) and i<10:
                logger.info("Calculate Phase again")
                Phase = []
                for k in range(1,4):
                    Phase.append(float(self.inst.query(CMD)))
                    time.sleep(0.1)
                MeanPhase = np.mean(Phase)
                StDevPhase = np.std(Phase)
                logger.info("Phase : %s - Mean : %s - StDev : %s" %(Phase,MeanPhase,StDevPhase))
                i += 1
                time.sleep((1+i)/10)
            cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='Find_Gain_Osc').id, value=1, start=time.time())
            cwt.save()
#            self.write_data("find_gain", 1)
            return self.parse_value(MeanPhase)
        elif variable_id == 'find_gain':
            CMD = str(':MEASUrement:IMMed:SOUrce1 CH1;:MEASUREMENT:IMMED:TYPE PK2PK;:MEASUREMENT:IMMED:VALUE?')
            P2P1 = self.inst.query(CMD)
            try:
                float(P2P1)
                i = 12
            except:
                i = 0
                logger.error("i : %s" % i)
            while i < 10:
                try:
                    P2P1 = self.inst.query('MEASUREMENT:IMMED:VALUE?')
                    logger.info("P2P1 : %s" % P2P2)
                    float(P2P1)
                    i =12
                except:
                    i += 1
                    logger.error("P2P1 - i : %s" % i)

            CMD = str(':MEASUrement:IMMed:SOUrce1 CH2;:MEASUREMENT:IMMED:TYPE PK2PK;:MEASUREMENT:IMMED:VALUE?')
            P2P2 = self.inst.query(CMD)
            try:
                float(P2P2)
                i = 12
            except:
                i = 0
                logger.error("i : %s" %(i))
            while i < 10:
                try:
                    P2P2 = self.inst.query('MEASUREMENT:IMMED:VALUE?')
                    logger.info("P2P2 : %s" % P2P2)
                    float(P2P2)
                    i =12
                except:
                    i += 1
                    logger.error("P2P2 - i : %s" % i)

            try:
                float(P2P2)
                float(P2P1)
            except:
                return None
            G = 20*log10(float(P2P2)/float(P2P1))
            # self.inst.write('SELect:CH1 0')
            # self.inst.write('SELect:CH2 0')
            N = RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_n').id)
            N_new = N.value() + 1
            F = RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_F').id)
            Fmin = RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_Fmin').id)
            Fmax = RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_Fmax').id)
            nb_points = RecordedData.objects.last_element(variable_id=Variable.objects.get(name='BODE_nb_points').id)
            # Variation de F en log
            k=pow(Fmax.value()/Fmin.value(),(N_new-11)/(nb_points.value()-1))
            F_new = Fmin.value()*pow(Fmax.value()/Fmin.value(),(N_new-1)/(nb_points.value()-1))
            F_new = int(F_new)
#            logger.info("N_new : %s - k : %s - F : %s" %(N_new, k, F_new))
            # Variation F linéaire
            # F_new = F.value() + (Fmax.value() - Fmin.value())/nb_points.value()
            if F_new > Fmax.value():
                logger.info("BODE terminé")
            else:
                cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='BODE_F').id, value=F_new,
                                      start=time.time())
                cwt.save()
                cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='BODE_n').id, value=N_new,
                                      start=time.time())
                cwt.save()
                cwt = DeviceWriteTask(variable_id=Variable.objects.get(name='Set_Freq_GBF').id, value=F_new,
                                      start=time.time())
                cwt.save()
            return self.parse_value(G)
        return self.parse_value(self.inst.query(str(variable_id)+' '+str(value)))

    def parse_value(self, value):
        """
        takes a string in the Tektronix MDO3014 format and returns a float value or None if not parseable
        """
        try:
            return float(value)
        except:
            return None

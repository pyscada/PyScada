# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, Device, DeviceHandler
from . import PROTOCOL_ID

from django.db import models
from django.db.models.signals import post_save

import logging

logger = logging.getLogger(__name__)


class VISAVariable(models.Model):
    visa_variable = models.OneToOneField(Variable, on_delete=models.CASCADE)
    variable_type_choices = ((0, 'configuration'), (1, 'acquisition'), (2, 'status'))
    variable_type = models.SmallIntegerField(choices=variable_type_choices)
    device_property = models.CharField(default='present_value', max_length=255,
                                       help_text='name of the Property the variable be assigned to')

    protocol_id = PROTOCOL_ID

    def __str__(self):
        return self.visa_variable.name


class VISADevice(models.Model):
    visa_device = models.OneToOneField(Device, on_delete=models.CASCADE)
    resource_name = models.CharField(max_length=255,
                                     default='GPIB0::22::INSTR',
                                     help_text=""" 'Examles for:\nGPIB0::22::INSTR' for GPIB Instrument\n
                                      'TCPIP::192.168.228.104::INSTR' for TCPIP/LXI Intruments\n 
                                      'USB0::0x1AB1::0x4CE::DS1ZA181806919::INSTR'\n 
                                      'ASRL/dev/ttyUSB0::INSTR'\n 
                                      http://pyvisa.readthedocs.io/en/stable/names.html""")

    instrument_handler = models.ForeignKey(DeviceHandler, null=True, blank=True, on_delete=models.SET_NULL)

    protocol_id = PROTOCOL_ID

    def parent_device(self):
        try:
            return self.visa_device
        except:
            return None

    def __str__(self):
        return self.visa_device.short_name


class ExtendedVISADevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'VISA Device'
        verbose_name_plural = 'VISA Devices'


class ExtendedVISAVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'VISA Variable'
        verbose_name_plural = 'VISA Variable'

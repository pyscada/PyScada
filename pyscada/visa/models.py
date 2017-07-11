# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, Device
from pyscada.models import BackgroundTask

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible

from time import time


@python_2_unicode_compatible
class VISAVariable(models.Model):
    visa_variable = models.OneToOneField(Variable)
    variable_type_choices = ((0, 'configuration'), (1, 'acquisition'), (2, 'status'))
    variable_type = models.SmallIntegerField(default=1, choices=variable_type_choices)
    device_property = models.CharField(default='present_value', max_length=255,
                                       help_text='name of the Property the variable be assigned to')

    def __str__(self):
        return self.visa_variable.name


@python_2_unicode_compatible
class VISADevice(models.Model):
    visa_device = models.OneToOneField(Device)
    resource_name = models.CharField(max_length=255,
                                     default='GPIB0::22::INSTR',
                                     help_text=" 'Examles for:\nGPIB0::22::INSTR' for GPIB Instrument\n 'TCPIP::192.168.228.104::INSTR' for TCPIP/LXI Intruments\n 'USB0::0x1AB1::0x4CE::DS1ZA181806919::INSTR'\n 'ASRL/dev/ttyUSB0::INSTR'\n http://pyvisa.readthedocs.io/en/stable/names.html")
    instrument = models.ForeignKey('VISADeviceHandler')

    def __str__(self):
        return self.visa_device.short_name


@python_2_unicode_compatible
class VISADeviceHandler(models.Model):
    name = models.CharField(default='', max_length=255)
    handler_class = models.CharField(default='pyscada.visa.devices.HP3456A', max_length=255,
                                     help_text='a Base class to extend can be found at pyscada.visa.devices.GenericDevice')
    handler_path = models.CharField(default=None, max_length=255, null=True, blank=True, help_text='')  # todo help

    def __str__(self):
        return self.name


@receiver(post_save, sender=VISAVariable)
@receiver(post_save, sender=VISADevice)
@receiver(post_save, sender=VISADeviceHandler)
def _reinit_daq_daemons(sender, **kwargs):
    """
    update the daq daemon configuration wenn changes be applied in the models
    """
    BackgroundTask.objects.filter(label='pyscada.daq.daemon',
                                  done=0,
                                  failed=0).update(message='reinit', restart_daemon=True, timestamp=time())

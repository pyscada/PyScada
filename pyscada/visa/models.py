# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, Device

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class VISAVariable(models.Model):
    visa_variable = models.OneToOneField(Variable)
    variable_type_choices = ((0, 'configuration'), (1, 'acquisition'), (2, 'status'))
    variable_type = models.SmallIntegerField(choices=variable_type_choices)
    device_property = models.CharField(default='present_value', max_length=255,
                                       help_text='name of the Property the variable be assigned to')

    def __str__(self):
        return self.visa_variable.name


@python_2_unicode_compatible
class VISADevice(models.Model):
    visa_device = models.OneToOneField(Device)
    resource_name = models.CharField(max_length=255,
                                     default='GPIB0::22::INSTR',
                                     help_text=""" 'Examles for:\nGPIB0::22::INSTR' for GPIB Instrument\n
                                      'TCPIP::192.168.228.104::INSTR' for TCPIP/LXI Intruments\n 
                                      'USB0::0x1AB1::0x4CE::DS1ZA181806919::INSTR'\n 
                                      'ASRL/dev/ttyUSB0::INSTR'\n 
                                      http://pyvisa.readthedocs.io/en/stable/names.html""")

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


@receiver(post_save, sender=VISAVariable)
@receiver(post_save, sender=VISADevice)
@receiver(post_save, sender=VISADeviceHandler)
@receiver(post_save, sender=ExtendedVISAVariable)
@receiver(post_save, sender=ExtendedVISADevice)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is VISADevice:
        post_save.send_robust(sender=Device, instance=instance.visa_device)
    elif type(instance) is VISAVariable:
        post_save.send_robust(sender=Variable, instance=instance.visa_variable)
    elif type(instance) is VISADeviceHandler:
        # todo
        pass
    elif type(instance) is ExtendedVISAVariable:
        post_save.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedVISADevice:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))

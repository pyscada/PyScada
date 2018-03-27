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
class OneWireVariable(models.Model):
    onewire_variable = models.OneToOneField(Variable)
    address = models.CharField(default='', max_length=400, help_text='64bit Sensor Address')
    sensor_type_choices = (('DS18B20', 'DS18B20 Temperature Sensor'),)
    sensor_type = models.CharField(default='', max_length=10, choices=sensor_type_choices)

    def __str__(self):
        return self.onewire_variable.name


@python_2_unicode_compatible
class OneWireDevice(models.Model):
    onewire_device = models.OneToOneField(Device)
    adapter_type_choices = (('owserver', 'OWFS owserver'), ('rpi_gpio4', 'RPi GPIO 4'),)
    adapter_type = models.CharField(default='', max_length=400, choices=adapter_type_choices)
    config = models.CharField(default='', max_length=400, blank=True,
                              help_text='for OWFS owserver: hostname:port, default is localhost:4304')

    def __str__(self):
        return self.onewire_device.short_name


class ExtendedOneWireDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'OneWire Device'
        verbose_name_plural = 'OneWire Devices'


class ExtendedOneWireVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'OneWire Variable'
        verbose_name_plural = 'OneWire Variable'


@receiver(post_save, sender=OneWireVariable)
@receiver(post_save, sender=OneWireDevice)
@receiver(post_save, sender=ExtendedOneWireDevice)
@receiver(post_save, sender=ExtendedOneWireVariable)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is OneWireDevice:
        post_save.send_robust(sender=Device, instance=instance.modbus_device)
    elif type(instance) is OneWireVariable:
        post_save.send_robust(sender=Variable, instance=instance.modbus_variable)
    elif type(instance) is ExtendedOneWireVariable:
        post_save.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedOneWireDevice:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))
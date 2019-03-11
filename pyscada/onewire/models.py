# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, Device

from django.db import models
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


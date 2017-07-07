# -*- coding: utf-8 -*-
from pyscada.models import Variable, Device
from pyscada.models import BackgroundTask

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from time import time


class OneWireVariable(models.Model):
    onewire_variable = models.OneToOneField(Variable)
    address = models.CharField(default='',max_length=400,help_text='64bit Sensor Address')
    sensor_type_choices = (('DS18B20','DS18B20 Temperature Sensor'),)
    sensor_type = models.CharField(default='',max_length=10,choices=sensor_type_choices)

    def __str__(self):
        return self.onewire_variable.name


class OneWireDevice(models.Model):
    onewire_device = models.OneToOneField(Device)
    adapter_type_choices = (('owserver','OWFS owserver'),('rpi_gpio4','RPi GPIO 4'),)
    adapter_type = models.CharField(default='',max_length=400,choices=adapter_type_choices)
    config = models.CharField(default='',max_length=400,blank=True,help_text='for OWFS owserver: hostname:port, default is localhost:4304')

@receiver(post_save, sender=OneWireVariable)
@receiver(post_save, sender=OneWireDevice)
def _reinit_daq_daemons(sender, **kwargs):
    """
    update the daq daemon configuration wenn changes be applied in the models
    """
    BackgroundTask.objects.filter(label='pyscada.daq.daemon',
                                  done=0, failed=0).update(message='reinit', restart_daemon=True, timestamp=time())
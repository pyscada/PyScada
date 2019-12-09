from __future__ import unicode_literals

from pyscada.models import Device
from pyscada.models import Variable

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class SMbusDevice(models.Model):
    smbus_device = models.OneToOneField(Device, on_delete=models.CASCADE)
    device_type_choices = (('ups_pico', 'UPS PIco'),)
    device_type = models.CharField(max_length=400, choices=device_type_choices)
    port = models.CharField(default='1', max_length=400, )
    address_choices = [(i, '0x%s/%d' % (hex(i), i)) for i in range(256)]
    address = models.PositiveSmallIntegerField(default=None, choices=address_choices, null=True)

    def __str__(self):
        return self.smbus_device.short_name


@python_2_unicode_compatible
class SMbusVariable(models.Model):
    smbus_variable = models.OneToOneField(Variable, on_delete=models.CASCADE)
    information = models.CharField(default='None', max_length=400, )

    def __str__(self):
        return self.smbus_variable.short_name


class ExtendedSMBusDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'SMBus Device'
        verbose_name_plural = 'SMBus Devices'


class ExtendedSMbusVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'SMBus Variable'
        verbose_name_plural = 'SMBus Variables'

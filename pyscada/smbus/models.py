from __future__ import unicode_literals

from pyscada.models import Device
from pyscada.models import Variable

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.signals import post_save
import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class SMBusDevice(models.Model):
    smbus_device = models.OneToOneField(Device, on_delete=models.CASCADE)
    instrument = models.ForeignKey('SMBusDeviceHandler', null=True, on_delete=models.SET_NULL)
    port = models.CharField(default='1', max_length=400, )
    address_choices = [(i, '0x%s/%d' % (hex(i), i)) for i in range(256)]
    address = models.PositiveSmallIntegerField(default=None, choices=address_choices, null=True)

    def __str__(self):
        return self.smbus_device.short_name


@python_2_unicode_compatible
class SMBusVariable(models.Model):
    smbus_variable = models.OneToOneField(Variable, on_delete=models.CASCADE)
    information = models.CharField(default='None', max_length=400, )

    def __str__(self):
        return self.smbus_variable.short_name


@python_2_unicode_compatible
class SMBusDeviceHandler(models.Model):
    name = models.CharField(default='', max_length=255)
    handler_class = models.CharField(default='pyscada.smbus.devices.ups_pico', max_length=255,
                                     help_text='a Base class to extend can be found at pyscada.smbus.devices.GenericDevice')
    handler_path = models.CharField(default=None, max_length=255, null=True, blank=True, help_text='')  # todo help

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # TODO : select only devices of selected variables
        post_save.send_robust(sender=SMBusDeviceHandler, instance=SMBusDevice.objects.first())
        super(SMBusDeviceHandler, self).save(*args, **kwargs)


class ExtendedSMBusDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'SMBus Device'
        verbose_name_plural = 'SMBus Devices'


class ExtendedSMBusVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'SMBus Variable'
        verbose_name_plural = 'SMBus Variables'

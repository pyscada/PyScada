from __future__ import unicode_literals

from pyscada.models import Device
from pyscada.models import Variable

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class SMbusDevice(models.Model):
    smbus_device = models.OneToOneField(Device)
    device_type_choices = (('ups_pico', 'UPS PIco'),)
    device_type = models.CharField(max_length=400, choices=device_type_choices)
    port = models.CharField(default='1', max_length=400, )
    address_choices = [(i, '0x%s/%d' % (hex(i), i)) for i in range(256)]
    address = models.PositiveSmallIntegerField(default=None, choices=address_choices, null=True)

    def __str__(self):
        return self.smbus_device.short_name


@python_2_unicode_compatible
class SMbusVariable(models.Model):
    smbus_variable = models.OneToOneField(Variable)
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


@receiver(post_save, sender=SMbusVariable)
@receiver(post_save, sender=SMbusDevice)
@receiver(post_save, sender=ExtendedSMBusDevice)
@receiver(post_save, sender=ExtendedSMbusVariable)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is SMbusDevice:
        post_save.send_robust(sender=Device, instance=instance.smbus_device)
    elif type(instance) is SMbusVariable:
        post_save.send_robust(sender=Variable, instance=instance.smbus_variable)
    elif type(instance) is ExtendedSMbusVariable:
        post_save.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedSMBusDevice:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))
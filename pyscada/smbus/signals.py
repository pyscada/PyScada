# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, Device
from pyscada.smbus.models import SMbusVariable, SMbusDevice, ExtendedSMBusDevice, ExtendedSMbusVariable

from django.dispatch import receiver
from django.db.models.signals import post_save

import logging

logger = logging.getLogger(__name__)



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

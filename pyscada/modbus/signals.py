# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable
from pyscada.modbus.models import ModbusDevice, ModbusVariable, ExtendedModbusDevice, ExtendedModbusVariable

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ModbusDevice)
@receiver(post_save, sender=ModbusVariable)
@receiver(post_save, sender=ExtendedModbusDevice)
@receiver(post_save, sender=ExtendedModbusVariable)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is ModbusDevice:
        post_save.send_robust(sender=Device, instance=instance.modbus_device)
    elif type(instance) is ModbusVariable:
        post_save.send_robust(sender=Variable, instance=instance.modbus_variable)
    elif type(instance) is ExtendedModbusVariable:
        post_save.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedModbusDevice:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))


@receiver(pre_delete, sender=ModbusDevice)
@receiver(pre_delete, sender=ModbusVariable)
@receiver(pre_delete, sender=ExtendedModbusDevice)
@receiver(pre_delete, sender=ExtendedModbusVariable)
def _del_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is ModbusDevice:
        pre_delete.send_robust(sender=Device, instance=instance.modbus_device)
    elif type(instance) is ModbusVariable:
        pre_delete.send_robust(sender=Variable, instance=instance.modbus_variable)
    elif type(instance) is ExtendedModbusVariable:
        pre_delete.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedModbusDevice:
        pre_delete.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))

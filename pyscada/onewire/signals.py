# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable
from pyscada.onewire.models import OneWireVariable, OneWireDevice, ExtendedOneWireDevice, ExtendedOneWireVariable

from django.dispatch import receiver
from django.db.models.signals import post_save

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=OneWireVariable)
@receiver(post_save, sender=OneWireDevice)
@receiver(post_save, sender=ExtendedOneWireDevice)
@receiver(post_save, sender=ExtendedOneWireVariable)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is OneWireDevice:
        post_save.send_robust(sender=Device, instance=instance.onewire_device)
    elif type(instance) is OneWireVariable:
        post_save.send_robust(sender=Variable, instance=instance.onewire_variable)
    elif type(instance) is ExtendedOneWireVariable:
        post_save.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedOneWireDevice:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))
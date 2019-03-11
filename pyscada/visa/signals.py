# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable
from pyscada.visa.models import VISAVariable, VISADevice, VISADeviceHandler, ExtendedVISAVariable, ExtendedVISADevice

from django.dispatch import receiver
from django.db.models.signals import post_save

import logging

logger = logging.getLogger(__name__)


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

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, Device
from pyscada.systemstat.models import SystemStatVariable, ExtendedSystemStatVariable, ExtendedSystemStatDevice

from django.dispatch import receiver
from django.db.models.signals import post_save

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SystemStatVariable)
@receiver(post_save, sender=ExtendedSystemStatVariable)
@receiver(post_save, sender=ExtendedSystemStatDevice)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is SystemStatVariable:
        post_save.send_robust(sender=Variable, instance=instance.system_stat_variable)
    elif type(instance) is ExtendedSystemStatVariable:
        post_save.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedSystemStatDevice:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))
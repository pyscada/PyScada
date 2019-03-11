# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, Device, Scaling, BackgroundProcess

from django.dispatch import receiver
from django.db.models.signals import post_save

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Variable)
@receiver(post_save, sender=Device)
@receiver(post_save, sender=Scaling)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is Device:
        try:
            bp = BackgroundProcess.objects.get(pk=instance.protocol_id)
        except:
            return False
        bp.restart()
    elif type(instance) is Variable:
        try:
            bp = BackgroundProcess.objects.get(pk=instance.device.protocol_id)
        except:
            return False
        bp.restart()
    elif type(instance) is Scaling:
        for bp_pk in list(instance.variable_set.all().values_list('device__protocol_id').distinct()):
            try:
                bp = BackgroundProcess.objects.get(pk=bp_pk)
            except:
                return False
            bp.restart()
    else:
        logger.debug('post_save from %s' % type(instance))

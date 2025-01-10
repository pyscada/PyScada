# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import (
    Variable,
    Device,
    Scaling,
    BackgroundProcess,
    VariableProperty,
    DeviceHandler,
)
from pyscada.admin import VariableState

from django.dispatch import receiver
from django.db.models.signals import (
    post_save,
    pre_delete,
)

import signal
import logging

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=Variable)
@receiver(post_save, sender=Variable)
def _variable(sender, instance, **kwargs):
    """
    Send signal to restart the bp associated for the device of this variable
    """
    if type(instance) is Variable or type(instance) is VariableState:
        logger.debug(
            f"post_save or pre_delete {type(instance).__name__}.{instance}-{getattr(instance, 'id', 'new')}"
        )
        try:
            post_save.send_robust(
                sender=type(instance.device), instance=instance.device
            )
        except Exception as e:
            logger.debug(e)


@receiver(pre_delete, sender=Scaling)
@receiver(post_save, sender=Scaling)
def _scaling(sender, instance, **kwargs):
    """
    Send signal to restart the bp associated for each device of a variable using this scaling
    """
    if type(instance) is Scaling:
        logger.debug(
            f"post_save or pre_delete {type(instance).__name__}.{instance}-{getattr(instance, 'id', 'new')}"
        )
        try:
            for variable in instance.variable_set.all():
                post_save.send_robust(
                    sender=type(variable.device), instance=variable.device
                )
        except Exception as e:
            logger.debug(e)


@receiver(pre_delete, sender=DeviceHandler)
@receiver(post_save, sender=DeviceHandler)
def _device_handler_post_save(sender, instance, **kwargs):
    """
    Send signal to restart the bp associated for each device using this device handler
    """
    if type(instance) is DeviceHandler:
        logger.debug(
            f"post_save or pre_delete {type(instance).__name__}.{instance}-{getattr(instance, 'id', 'new')}"
        )
        try:
            for device in instance.device_set.all():
                post_save.send_robust(sender=type(device), instance=device)
        except Exception as e:
            logger.debug(e)


@receiver(post_save, sender=VariableProperty)
def _vp_post_save(sender, instance, **kwargs):
    if type(instance) is VariableProperty:
        # TODO: handle VP change but no value change
        pass


@receiver(post_save, sender=Device)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    Update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is Device:
        logger.debug(
            f"post_save {type(instance).__name__}.{instance}-{getattr(instance, 'id', 'new')}"
        )
        try:
            bp = BackgroundProcess.objects.get(
                done=False,
                failed=False,
                label=f"pyscada.{instance.protocol.protocol}-{instance.id}",
            )
        except BackgroundProcess.DoesNotExist:
            try:
                # for modbus protocol
                bp = BackgroundProcess.objects.get(
                    done=False,
                    failed=False,
                    label__startswith=f"pyscada.{instance.protocol.protocol}-{instance.id}",
                )
            except BackgroundProcess.DoesNotExist:
                # new device, add it to the parent process list
                # todo select only one device not all for that protocol
                if instance.protocol_id == 1:
                    # generic device has no parent process to restart
                    return False
                try:
                    bp = BackgroundProcess.objects.get(pk=instance.protocol_id)
                except BackgroundProcess.DoesNotExist:
                    logger.debug(
                        f"BackgroundProcess for protocol {instance.protocol_id} not found"
                    )
                    return False
        except Exception as e:
            logger.debug(e)
            return False
        logger.debug(bp.label)
        bp.restart()
        return True
    else:
        logger.debug(f"Unknown post_save from {type(sender)} to {type(instance)}")


@receiver(pre_delete, sender=Device)
def _del_daq_daemons(sender, instance, **kwargs):
    """
    Delete the daq daemon when device is deleted
    """
    if type(instance) is Device:
        logger.debug(
            f"pre_delete {type(instance).__name__}.{instance}-{getattr(instance, 'id', 'new')}"
        )
        try:
            bp = BackgroundProcess.objects.get(
                done=False,
                failed=False,
                label=f"pyscada.{instance.protocol.protocol}-{instance.id}",
            )
        except BackgroundProcess.DoesNotExist:
            try:
                # for modbus protocol
                bp = BackgroundProcess.objects.get(
                    done=False,
                    failed=False,
                    label__startswith=f"pyscada.{instance.protocol.protocol}-{instance.id}",
                )
            except BackgroundProcess.DoesNotExist:
                # BP not created, cannot stop
                return False
        except Exception as e:
            logger.debug(e)
            return False
        bp.stop(signum=signal.SIGKILL)
        return True
    else:
        logger.debug(f"Unknown pre_delete from {type(sender)} to {type(instance)}")

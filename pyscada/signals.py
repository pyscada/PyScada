# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, Device, Scaling, BackgroundProcess, VariableProperty, DeviceHandler, RecordedData
from pyscada.admin import VariableState

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete, pre_save

import logging

logger = logging.getLogger(__name__)


#@receiver(pre_save, sender=VariableProperty)
def _vp_value_change(sender, instance, **kwargs):
    if type(instance) is VariableProperty:
        if instance.id is not None:  # existing object
            previous = VariableProperty.objects.get(id=instance.id)
            if str(instance.last_value) != str(previous.value()):
                logger.debug("VP %s new value = %s - %s" % (str(instance), instance.last_value, previous.value()))
                instance.last_value = str(previous.value())
                instance.value_changed = True


@receiver(post_save, sender=VariableProperty)
@receiver(post_save, sender=Variable)
@receiver(post_save, sender=Device)
@receiver(post_save, sender=Scaling)
@receiver(post_save, sender=DeviceHandler)
#@receiver(post_save, sender=RecordedData)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is Device:
        try:
            logger.debug("post_save pyscada." + str(instance.protocol.protocol) + "-" + str(instance.id))
            try:
                bp = BackgroundProcess.objects.get(
                    label="pyscada." + str(instance.protocol.protocol) + "-" + str(instance.id))
            except BackgroundProcess.DoesNotExist:
                # for modbus protocol
                bp = BackgroundProcess.objects.get(
                    label__startswith="pyscada." + str(instance.protocol.protocol) + "-" + str(
                        instance.id) + "-")
        except Exception as e:
            logger.debug("post_save pyscada")
            logger.debug(e)
            # new device, add it to the parent process list
            # todo select only one device not all for that protocol
            try:
                bp = BackgroundProcess.objects.get(pk=instance.protocol_id)
            except:
                return False
        bp.restart()
    elif type(instance) is Variable or type(instance) is VariableState:
        try:
            logger.debug("post_save pyscada." + str(instance.device.protocol.protocol) + "-" + str(instance.device_id))
            try:
                bp = BackgroundProcess.objects.get(
                    label="pyscada." + str(instance.device.protocol.protocol) + "-" + str(instance.device_id))
            except BackgroundProcess.DoesNotExist:
                # for modbus protocol
                bp = BackgroundProcess.objects.get(
                    label__startswith="pyscada." + str(instance.device.protocol.protocol) + "-" + str(
                        instance.device_id) + "-")
        except Exception as e:
            logger.debug(e)
            # todo select only one device not all for that protocol
            try:
                bp = BackgroundProcess.objects.get(pk=instance.device.protocol_id)
            except:
                return False
        bp.restart()
    elif type(instance) is Scaling:
        # todo select only one device not all for that protocol
        for bp_pk in list(instance.variable_set.all().values_list('device__protocol_id').distinct()):
            try:
                bp = BackgroundProcess.objects.get(pk=bp_pk)
            except:
                return False
            bp.restart()
    elif type(instance) is DeviceHandler:
        # todo
        logger.debug('post_save DeviceHandler from %s' % type(instance))
        pass
    elif type(instance) is VariableProperty:
        logger.debug('post_save from VP %s' % str(instance))
        return
        if instance.id is not None:  # existing object
            if instance.value_changed:
                instance.value_changed = False
                try:
                    logger.debug("post_save pyscada." + str(instance.variable.device.protocol.protocol) + "-" + str(instance.variable.device_id))
                    try:
                        bp = BackgroundProcess.objects.get(
                            label="pyscada." + str(instance.variable.device.protocol.protocol) + "-" + str(instance.variable.device_id))
                    except BackgroundProcess.DoesNotExist:
                        # for modbus protocol
                        bp = BackgroundProcess.objects.get(
                            label__startswith="pyscada." + str(instance.variable.device.protocol.protocol) + "-" + str(
                                instance.variable.device_id) + "-")
                except Exception as e:
                    logger.debug(e)
                    # todo select only one device not all for that protocol
                    try:
                        bp = BackgroundProcess.objects.get(pk=instance.variable.device.protocol_id)
                    except:
                        return False
                bp.restart()
            else:
                logger.debug("VP something changed (not value)")
    else:
        logger.debug('post_save from %s' % type(instance))


@receiver(pre_delete, sender=VariableProperty)
@receiver(pre_delete, sender=Variable)
@receiver(pre_delete, sender=Device)
@receiver(pre_delete, sender=Scaling)
@receiver(pre_delete, sender=DeviceHandler)
def _del_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is Device:
        try:
            logger.debug("pre_delete pyscada." + str(instance.protocol.protocol) + "-" + str(instance.id))
            try:
                bp = BackgroundProcess.objects.get(
                    label="pyscada." + str(instance.protocol.protocol) + "-" + str(instance.id))
            except BackgroundProcess.DoesNotExist:
                # for modbus protocol
                bp = BackgroundProcess.objects.get(
                    label__startswith="pyscada." + str(instance.protocol.protocol) + "-" + str(
                        instance.id) + "-")
        except Exception as e:
            logger.debug("pre_delete pyscada")
            logger.debug(e)
            return False
        bp.stop()
    elif type(instance) is Variable or type(instance) is VariableState:
        try:
            logger.debug("pre_delete pyscada." + str(instance.device.protocol.protocol) + "-" + str(instance.device_id))
            try:
                bp = BackgroundProcess.objects.get(
                    label="pyscada." + str(instance.device.protocol.protocol) + "-" + str(instance.device_id))
            except BackgroundProcess.DoesNotExist:
                # for modbus protocol
                bp = BackgroundProcess.objects.get(
                    label__startswith="pyscada." + str(instance.device.protocol.protocol) + "-" + str(
                        instance.device_id) + "-")
        except Exception as e:
            logger.debug(e)
            return False
        bp.restart()
    elif type(instance) is Scaling:
        # todo select only one device not all for that protocol
        for bp_pk in list(instance.variable_set.all().values_list('device__protocol_id').distinct()):
            try:
                bp = BackgroundProcess.objects.get(pk=bp_pk)
            except:
                return False
            bp.restart()
    elif type(instance) is DeviceHandler:
        # todo
        logger.debug('pre_delete DeviceHandler from %s' % type(instance))
        pass
    elif type(instance) is VariableProperty:
        try:
            logger.debug("pre_delete pyscada." + str(instance.variable.device.protocol.protocol) + "-" + str(instance.variable.device_id))
            try:
                bp = BackgroundProcess.objects.get(
                    label="pyscada." + str(instance.variable.device.protocol.protocol) + "-" + str(instance.variable.device_id))
            except BackgroundProcess.DoesNotExist:
                # for modbus protocol
                bp = BackgroundProcess.objects.get(
                    label__startswith="pyscada." + str(instance.variable.device.protocol.protocol) + "-" + str(
                        instance.device_id) + "-")
        except Exception as e:
            logger.debug(e)
            return False
        bp.restart()
    else:
        logger.debug('pre_delete from %s' % type(instance))

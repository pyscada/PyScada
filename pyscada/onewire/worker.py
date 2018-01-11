#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import Process as BaseDAQProcess
from pyscada.models import BackgroundProcess
from pyscada.onewire.models import OneWireDevice
import json
import logging

logger = logging.getLogger(__name__)


class Process(BaseDAQProcess):
    def __init__(self, dt=5, **kwargs):
        super(Process, self).__init__(dt=dt, **kwargs)
        self.ONEWIRE_PROCESSES = []

    def init_process(self):

        # clean up
        BackgroundProcess.objects.filter(parent_process__pk=self.process_id, done=False).delete()

        for item in OneWireDevice.objects.filter(onewire_device__active=True):
            # every device gets its own process
            bp = BackgroundProcess(label='pyscada.onewire-%s' % item.id,
                                   message='waiting..',
                                   enabled=True,
                                   parent_process_id=self.process_id,
                                   process_class='pyscada.utils.scheduler.SingleDeviceDAQProcess',
                                   process_class_kwargs=json.dumps(
                                       {'device_id': item.onewire_device.pk}))
            bp.save()
            self.ONEWIRE_PROCESSES.append({'id': bp.id,
                                           'key': item.id,
                                           'device_id': item.onewire_device.pk,
                                           'failed': 0})

    def loop(self):
        """
        
        """
        # check if all onewire processes are running
        for onewire_process in self.ONEWIRE_PROCESSES:
            try:
                BackgroundProcess.objects.get(pk=onewire_process['id'])
            except BackgroundProcess.DoesNotExist or BackgroundProcess.MultipleObjectsReturned:
                # Process is dead, spawn new instance
                if onewire_process['failed'] < 3:
                    bp = BackgroundProcess(label='pyscada.visa-%s' % onewire_process['key'],
                                           message='waiting..',
                                           enabled=True,
                                           parent_process_id=self.process_id,
                                           process_class='pyscada.utils.scheduler.SingleDeviceDAQProcess',
                                           process_class_kwargs=json.dumps(
                                               {'device_id': onewire_process['device_id']}))
                    bp.save()
                    onewire_process['id'] = bp.id
                    onewire_process['failed'] += 1
                else:
                    logger.error('process pyscada.onewire-%s failed more then 3 times' % onewire_process['key'])

        return 1, None

    def cleanup(self):
        # todo cleanup
        pass

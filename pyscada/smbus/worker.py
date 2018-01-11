#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import Process as BaseDAQProcess
from pyscada.models import BackgroundProcess
from pyscada.smbus.models import SMbusDevice

import json
import logging

logger = logging.getLogger(__name__)


class Process(BaseDAQProcess):
    def __init__(self, dt=5, **kwargs):
        super(Process, self).__init__(dt=dt, **kwargs)
        self.SMbus_PROCESSES = []

    def init_process(self):
        setattr(self, 'SMbus_PROCESSES', [])

        # clean up
        BackgroundProcess.objects.filter(parent_process__pk=self.process_id, done=False).delete()

        for item in SMbusDevice.objects.filter(smbus_device__active=True):
            # every device gets its own process
            bp = BackgroundProcess(label='pyscada.smbus-%s' % item.id,
                                   message='waiting..',
                                   enabled=True,
                                   parent_process_id=self.process_id,
                                   process_class='pyscada.utils.scheduler.SingleDeviceDAQProcess',
                                   process_class_kwargs=json.dumps(
                                       {'device_id': item.smbus_device.pk}))
            bp.save()
            self.SMbus_PROCESSES.append({'id': bp.id,
                                         'key': item.id,
                                         'failed': 0,
                                         'device_id': item.smbus_device.pk})

    def loop(self):
        """
        
        """
        # check if all smbus processes are running
        for smbus_process in self.SMbus_PROCESSES:
            try:
                BackgroundProcess.objects.get(pk=smbus_process['id'])
            except BackgroundProcess.DoesNotExist or BackgroundProcess.MultipleObjectsReturned:
                # Process is dead, spawn new instance
                if smbus_process['failed'] < 3:
                    bp = BackgroundProcess(label='pyscada.smbus-%s' % smbus_process['key'],
                                           message='waiting..',
                                           enabled=True,
                                           parent_process_id=self.process_id,
                                           process_class='pyscada.utils.scheduler.SingleDeviceDAQProcess',
                                           process_class_kwargs=json.dumps(
                                               {'device_id': smbus_process['device_id']}))
                    bp.save()
                    smbus_process['id'] = bp.id
                    smbus_process['failed'] += 1
                else:
                    logger.error('process pyscada.smbus-%s failed more then 3 times' % smbus_process['key'])

        return 1, None

    def cleanup(self):
        # todo cleanup
        pass

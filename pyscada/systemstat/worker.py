#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.utils.scheduler import Process as BaseDAQProcess
from pyscada.models import BackgroundProcess, Device
from pyscada.systemstat import PROTOCOL_ID
import json
import traceback
import logging

logger = logging.getLogger(__name__)


class Process(BaseDAQProcess):
    def __init__(self, dt=5, **kwargs):
        super(Process, self).__init__(dt=dt, **kwargs)
        self.SYSTEMSTAT_PROCESSES = []

    def init_process(self):

        # clean up
        BackgroundProcess.objects.filter(parent_process__pk=self.process_id, done=False).delete()

        for item in Device.objects.filter(active=True, protocol_id=PROTOCOL_ID):
            # every device gets its own process
            bp = BackgroundProcess(label='pyscada.systemstat-%s' % item.id,
                                   message='waiting..',
                                   enabled=True,
                                   parent_process_id=self.process_id,
                                   process_class='pyscada.utils.scheduler.SingleDeviceDAQProcess',
                                   process_class_kwargs=json.dumps(
                                       {'device_id': item.pk}))
            bp.save()
            self.SYSTEMSTAT_PROCESSES.append({'id': bp.id,
                                              'key': item.id,
                                              'device_id': item.pk,
                                              'failed': 0})

    def loop(self):
        """
        
        """
        # check if all systemstat processes are running
        for systemstat_process in self.SYSTEMSTAT_PROCESSES:
            try:
                BackgroundProcess.objects.get(pk=systemstat_process['id'])
            except BackgroundProcess.DoesNotExist or BackgroundProcess.MultipleObjectsReturned:
                # Process is dead, spawn new instance
                if systemstat_process['failed'] < 3:
                    bp = BackgroundProcess(label='pyscada.systemstat-%s' % systemstat_process['key'],
                                           message='waiting..',
                                           enabled=True,
                                           parent_process_id=self.process_id,
                                           process_class='pyscada.utils.scheduler.SingleDeviceDAQProcess',
                                           process_class_kwargs=json.dumps(
                                               {'device_id': systemstat_process['device_id']}))
                    bp.save()
                    systemstat_process['id'] = bp.id
                    systemstat_process['failed'] += 1
                else:
                    logger.error('process pyscada.systemstat-%s failed more then 3 times' % systemstat_process['key'])

        return 1, None

    def cleanup(self):
        # todo cleanup
        pass

    def restart(self):
        for systemstat_process in self.SYSTEMSTAT_PROCESSES:
            try:
                bp = BackgroundProcess.objects.get(pk=systemstat_process['id'])
                bp.restart()
            except:
                logger.debug('%s, unhandled exception\n%s' % (self.label, traceback.format_exc()))

        return False

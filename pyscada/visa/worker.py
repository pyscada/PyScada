#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import Process as BaseDAQProcess
from pyscada.models import BackgroundProcess
from pyscada.visa.models import VISADevice
import json
import traceback
import logging

logger = logging.getLogger(__name__)


class Process(BaseDAQProcess):
    def __init__(self, dt=5, **kwargs):
        super(Process, self).__init__(dt=dt, **kwargs)
        self.VISA_PROCESSES = []

    def init_process(self):

        # clean up
        BackgroundProcess.objects.filter(parent_process__pk=self.process_id, done=False).delete()

        for item in VISADevice.objects.filter(visa_device__active=True):
            # every device gets its own process
            bp = BackgroundProcess(label='pyscada.visa-%s' % item.id,
                                   message='waiting..',
                                   enabled=True,
                                   parent_process_id=self.process_id,
                                   process_class='pyscada.utils.scheduler.SingleDeviceDAQProcess',
                                   process_class_kwargs=json.dumps(
                                       {'device_id': item.visa_device.pk}))
            bp.save()
            self.VISA_PROCESSES.append({'id': bp.id,
                                        'key': item.id,
                                        'device_id': item.visa_device.pk,
                                        'failed': 0})

    def loop(self):
        """
        
        """
        # check if all visa processes are running
        for visa_process in self.VISA_PROCESSES:
            try:
                BackgroundProcess.objects.get(pk=visa_process['id'])
            except BackgroundProcess.DoesNotExist or BackgroundProcess.MultipleObjectsReturned:
                # Process is dead, spawn new instance
                if visa_process['failed'] < 3:
                    bp = BackgroundProcess(label='pyscada.visa-%s' % visa_process['key'],
                                           message='waiting..',
                                           enabled=True,
                                           parent_process_id=self.process_id,
                                           process_class='pyscada.utils.scheduler.SingleDeviceDAQProcess',
                                           process_class_kwargs=json.dumps(
                                               {'device_id': visa_process['device_id']}))
                    bp.save()
                    visa_process['id'] = bp.id
                    visa_process['failed'] += 1
                else:
                    logger.debug('process pyscada.visa-%s failed more then 3 times' % visa_process['key'])

        return 1, None

    def cleanup(self):
        # todo cleanup
        pass

    def restart(self):
        for visa_process in self.VISA_PROCESSES:
            try:
                bp = BackgroundProcess.objects.get(pk=visa_process['id'])
                bp.restart()
            except:
                logger.debug('%s, unhandled exception\n%s' % (self.label, traceback.format_exc()))

        return False

#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import Process as BaseDAQProcess
from pyscada.models import BackgroundProcess
from pyscada.modbus.models import ModbusDevice
# from pyscada import log

import errno
from os import kill
import traceback
import json
import logging


logger = logging.getLogger(__name__)


class Process(BaseDAQProcess):
    def __init__(self, dt=5, **kwargs):
        super(Process, self).__init__(dt=dt, **kwargs)
        self.MODBUS_PROCESSES = []

    def init_process(self):
        for process in BackgroundProcess.objects.filter(parent_process__pk=self.process_id, done=False):
            try:
                kill(process.pid, 0)
            except OSError as e:
                if e.errno == errno.ESRCH:
                    process.delete()
                    continue
            logger.debug('process %d is alive' % process.pk)
            process.stop()

        # clean up
        BackgroundProcess.objects.filter(parent_process__pk=self.process_id, done=False).delete()

        grouped_ids = {}
        for item in ModbusDevice.objects.filter(modbus_device__active=True):
            if item.protocol == 0:  # Modbus IP
                # every device gets its own process
                grouped_ids['%d-%s:%s-%d' % (item.modbus_device.pk, item.ip_address, item.port, item.unit_id)] = [item]
                continue

            # every port gets its own process
            if item.port not in grouped_ids:
                grouped_ids[item.port] = []
            grouped_ids[item.port].append(item)

        for key, values in grouped_ids.items():
            bp = BackgroundProcess(label='pyscada.modbus-%s' % key,
                                   message='waiting..',
                                   enabled=True,
                                   parent_process_id=self.process_id,
                                   process_class='pyscada.utils.scheduler.MultiDeviceDAQProcess',
                                   process_class_kwargs=json.dumps(
                                       {'device_ids': [i.modbus_device.pk for i in values]}))
            bp.save()
            self.MODBUS_PROCESSES.append({'id': bp.id,
                                          'key': key,
                                          'device_ids': [i.modbus_device.pk for i in values],
                                          'failed': 0})

    def loop(self):
        """
        
        """
        # check if all modbus processes are running
        for modbus_process in self.MODBUS_PROCESSES:
            try:
                BackgroundProcess.objects.get(pk=modbus_process['id'])
            except BackgroundProcess.DoesNotExist or BackgroundProcess.MultipleObjectsReturned:
                # Process is dead, spawn new instance
                if modbus_process['failed'] < 3:
                    bp = BackgroundProcess(label='pyscada.modbus-%s' % modbus_process['key'],
                                           message='waiting..',
                                           enabled=True,
                                           parent_process_id=self.process_id,
                                           process_class='pyscada.utils.scheduler.MultiDeviceDAQProcess',
                                           process_class_kwargs=json.dumps(
                                               {'device_ids': modbus_process['device_ids']}))
                    bp.save()
                    modbus_process['id'] = bp.id
                    modbus_process['failed'] += 1
                else:
                    logger.error('process pyscada.modbus-%s failed more then 3 times' % modbus_process['key'])
            except:
                logger.debug('%s, unhandled exception\n%s' % (self.label, traceback.format_exc()))

        return 1, None

    def cleanup(self):
        # todo cleanup
        pass

    def restart(self):
        for modbus_process in self.MODBUS_PROCESSES:
            try:
                bp = BackgroundProcess.objects.get(pk=modbus_process['id'])
                bp.restart()
            except:
                logger.debug('%s, unhandled exception\n%s' % (self.label, traceback.format_exc()))

        return False

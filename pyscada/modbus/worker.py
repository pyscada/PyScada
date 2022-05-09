#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import MultiDeviceDAQProcessWorker
from pyscada.modbus import PROTOCOL_ID

import logging


logger = logging.getLogger(__name__)


class Process(MultiDeviceDAQProcessWorker):
    device_filter = dict(modbusdevice__isnull=False, protocol_id=PROTOCOL_ID)
    bp_label = 'pyscada.modbus-%s'

    def __init__(self, dt=5, **kwargs):
        super(MultiDeviceDAQProcessWorker, self).__init__(dt=dt, **kwargs)

    def gen_group_id(self, item):
        if item.modbusdevice.protocol == 0:  # Modbus IP
            # every device gets its own process
            return '%d-%s:%s-%d' % (item.pk,
                                    item.modbusdevice.ip_address,
                                    item.modbusdevice.port,
                                    item.modbusdevice.unit_id)
        else:
            # every port gets its own process
            return '%s' % item.modbusdevice.port

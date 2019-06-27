#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import SingleDeviceDAQProcessWorker

import logging


logger = logging.getLogger(__name__)


class Process(SingleDeviceDAQProcessWorker):
    device_filter = dict(onewiredevice__isnull=False)
    bp_label = 'pyscada.onewire-%s'

    def __init__(self, dt=5, **kwargs):
        super(SingleDeviceDAQProcessWorker, self).__init__(dt=dt, **kwargs)

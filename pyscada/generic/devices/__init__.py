# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .. import PROTOCOL_ID
from pyscada.models import DeviceProtocol
from pyscada.device import GenericHandlerDevice

from django.conf import settings

driver_ok = True

import logging

logger = logging.getLogger(__name__)


class GenericDevice(GenericHandlerDevice):
    def __init__(self, pyscada_device, variables):
        super().__init__(pyscada_device, variables)
        self._protocol = PROTOCOL_ID
        self.driver_ok = driver_ok

    def connect(self):
        return True

    def read_data(self, variable_instance):
        """
        Generic dummy device : Don't read nothing.
        """
        return None

    def write_data(self, variable_id, value, task):
        """
        Generic dummy device : Don't write nothing.
        """
        return None

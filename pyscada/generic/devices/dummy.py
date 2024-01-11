# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.generic.devices import GenericDevice
import logging

logger = logging.getLogger(__name__)


class Handler(GenericDevice):
    """
    Generic dummy device
    """

    def write_data(self, variable_id, value, task):
        """
        Generic dummy device : return the value to write.
        """
        return value

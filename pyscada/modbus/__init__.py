# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pyscada

__version__ = pyscada.__version__
__author__ = pyscada.__author__

default_app_config = 'pyscada.modbus.apps.PyScadaModbusConfig'

PROTOCOL_ID = 3

parent_process_list = [{'pk': PROTOCOL_ID,
                        'label': 'pyscada.modbus',
                        'process_class': 'pyscada.modbus.worker.Process',
                        'process_class_kwargs': '{"dt_set":30}',
                        'enabled': True}]

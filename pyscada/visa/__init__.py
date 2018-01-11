# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pyscada

__version__ = pyscada.__version__
__author__ = pyscada.__author__

PROTOCOL_ID = 5

default_app_config = 'pyscada.visa.apps.PyScadaVISAConfig'

parent_process_list = [{'pk':PROTOCOL_ID,
                        'label': 'pyscada.visa',
                        'process_class': 'pyscada.visa.worker.Process',
                        'process_class_kwargs': '{"dt_set":30}',
                        'enabled': True}]
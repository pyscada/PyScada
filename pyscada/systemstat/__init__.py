# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada import core

__version__ = core.__version__
__author__ = core.__author__

PROTOCOL_ID = 2

default_app_config = 'pyscada.systemstat.apps.PyScadaSystemstatConfig'

parent_process_list = [{'pk': PROTOCOL_ID,
                        'label': 'pyscada.systemstat',
                        'process_class': 'pyscada.systemstat.worker.Process',
                        'process_class_kwargs': '{"dt_set":30}',
                        'enabled': True}]

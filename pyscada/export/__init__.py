# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pyscada


__version__ = pyscada.__version__
__author__ = pyscada.__author__

default_app_config = 'pyscada.export.apps.PyScadaExportConfig'

parent_process_list = [{'label': 'pyscada.export',
                        'process_class': 'pyscada.export.worker.MasterProcess',
                        'process_class_kwargs': '{"dt_set":30}',
                        'enabled': True}]
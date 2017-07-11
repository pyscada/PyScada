# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '0.7.0b20'
__author__ = 'Martin Schröder'

default_app_config = 'pyscada.apps.PyScadaConfig'

parent_process_list = [{'label': 'pyscada.mail',
                        'process_class': 'pyscada.mail.Process',
                        'process_class_kwargs': '{"dt_set":30}',
                        'enabled': True},
                       {'label': 'pyscada.event',
                        'process_class': 'pyscada.event.Process',
                        'process_class_kwargs': '{"dt_set":5}',
                        'enabled': True}
                       ]


def version():
    return __version__

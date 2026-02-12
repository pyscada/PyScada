# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = "0.8.3"
__author__ = "Martin Schröder, Camille Lavayssiere"
__email__ = "team@pyscada.org"
__description__ = "PyScada a Python and Django based Open Source SCADA System"
__app_name__ = "PyScada"

default_app_config = "pyscada.apps.PyScadaConfig"
additional_installed_app = [
    "pyscada.core",
    "pyscada.hmi",
    "pyscada.export",
    "pyscada.django_datasource",
    "pyscada.cache_datasource",
    "pyscada.single_value_datasource"
    ]

parent_process_list = [
    {
        "pk": 97,
        "label": "pyscada.mail",
        "process_class": "pyscada.mail.worker.Process",
        "process_class_kwargs": '{"dt_set":30}',
        "enabled": True,
    },
    {
        "pk": 96,
        "label": "pyscada.event",
        "process_class": "pyscada.event.worker.Process",
        "process_class_kwargs": '{"dt_set":5}',
        "enabled": True,
    },
    {
        "pk": 16,
        "label": "pyscada.generic",
        "process_class": "pyscada.generic.worker.Process",
        "process_class_kwargs": '{"dt_set":5}',
        "enabled": True,
    },
]


def version():
    return __version__

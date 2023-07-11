# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pyscada import core


__version__ = core.__version__
__author__ = core.__author__

parent_process_list = [
    {
        "pk": 99,
        "label": "pyscada.export",
        "process_class": "pyscada.export.worker.MasterProcess",
        "process_class_kwargs": '{"dt_set":30}',
        "enabled": True,
    }
]

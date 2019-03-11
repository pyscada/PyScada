# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaModbusConfig(AppConfig):
    name = 'pyscada.modbus'
    verbose_name = _("PyScada Modbus Master/Client")

    def ready(self):
        import pyscada.modbus.signals
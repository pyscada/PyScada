# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaModbusConfig(AppConfig):
    name = 'pyscada.modbus'
    verbose_name = _("PyScada Modbus Master/Client")

# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaSMBusConfig(AppConfig):
    name = 'pyscada.smbus'
    verbose_name = _("PyScada SMBus Devices")

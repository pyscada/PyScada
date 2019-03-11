# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaOneWireConfig(AppConfig):
    name = 'pyscada.onewire'
    verbose_name = _("PyScada OneWire")

    def ready(self):
        import pyscada.onewire.signals

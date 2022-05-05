# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaVISAConfig(AppConfig):
    name = 'pyscada.visa'
    verbose_name = _("PyScada VISA")
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        import pyscada.visa.signals

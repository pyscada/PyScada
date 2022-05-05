# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaSystemstatConfig(AppConfig):
    name = 'pyscada.systemstat'
    verbose_name = _("PyScada System Statistics")
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        import pyscada.systemstat.signals

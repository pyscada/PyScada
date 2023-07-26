# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PyScadaHMIConfig(AppConfig):
    name = "pyscada.hmi"
    verbose_name = _("PyScada HMI")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import pyscada.hmi.signals

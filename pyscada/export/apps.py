# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaExportConfig(AppConfig):
    name = 'pyscada.export'
    verbose_name = _("PyScada Export")

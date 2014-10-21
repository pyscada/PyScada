# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaConfig(AppConfig):
    name = 'pyscada'
    verbose_name = _("PyScada Core")

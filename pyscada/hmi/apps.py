# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaHMIConfig(AppConfig):
    name = 'pyscada.hmi'
    verbose_name = _("PyScada HMI")

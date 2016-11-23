# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaPhantConfig(AppConfig):
    name = 'pyscada.phant'
    verbose_name = _("PyScada Phant Server")

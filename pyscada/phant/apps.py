# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PyScadaPhantConfig(AppConfig):
    name = 'pyscada.phant'
    verbose_name = _("PyScada Phant Server")
    default_auto_field = 'django.db.models.AutoField'

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
import logging

logger = logging.getLogger(__name__)


class PyScadaExportConfig(AppConfig):
    name = 'pyscada.export'
    verbose_name = _("PyScada Export")
    default_auto_field = 'django.db.models.AutoField'

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class PyScadaCacheDatasourceConfig(AppConfig):
    name = "pyscada.cache_datasource"
    verbose_name = _("PyScada Cache Datasource")
    default_auto_field = "django.db.models.AutoField"

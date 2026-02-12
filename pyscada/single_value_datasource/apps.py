# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class PyScada1SingleValueDatasourceConfig(AppConfig):
    name = "pyscada.single_value_datasource"
    verbose_name = _("PyScada Single Value Datasource")
    default_auto_field = "django.db.models.AutoField"

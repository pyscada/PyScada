# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.db.utils import ProgrammingError, OperationalError
import os
import logging

logger = logging.getLogger(__name__)


class PyScadaConfig(AppConfig):
    name = "pyscada"
    label = "pyscada"
    verbose_name = _("PyScada Core")
    path = os.path.dirname(os.path.realpath(__file__))
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import pyscada.signals

        try:
            from .hmi.models import Theme

            if Theme.objects.filter().count():
                Theme.objects.first().check_all_themes()
        except ProgrammingError:
            pass
        except OperationalError:
            pass

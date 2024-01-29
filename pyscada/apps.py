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
        except (ProgrammingError, OperationalError) as e:
            logger.debug(e)

        try:
            from .models import DataSourceModel, DataSource, DjangoDatabase

            # create the default data source model
            # only one data source linked to the RecordedData table can exist
            dsm, _ = DataSourceModel.objects.get_or_create(
                inline_model_name="DjangoDatabase",
                name="Django database",
                defaults={
                    # "name": "Django database",
                    "can_add": False,
                    "can_change": False,
                    "can_select": True,
                },
            )
            ds, _ = DataSource.objects.get_or_create(
                id=1,
                defaults={
                    "datasource_model": dsm,
                },
            )
            dd, _ = DjangoDatabase.objects.get_or_create(
                datasource=ds,
                defaults={
                    "data_model_app_name": "pyscada",
                    "data_model_name": "RecordedData",
                },
            )

            # For RecordedDataOld, hidden by default
            # set can_select to True to show it in the admin panel.
            # TODO : test read and write, test how it appears in the variable admin panel config if mannualy added (using shell)
            dsm, _ = DataSourceModel.objects.get_or_create(
                inline_model_name="DjangoDatabase",
                name="Django database hidden",
                defaults={
                    # "name": "Django database",
                    "can_add": False,
                    "can_change": False,
                    "can_select": False,
                },
            )
            ds, _ = DataSource.objects.get_or_create(
                datasource_model=dsm,
            )
            dd, _ = DjangoDatabase.objects.get_or_create(
                datasource=ds,
                defaults={
                    "data_model_app_name": "pyscada",
                    "data_model_name": "RecordedDataOld",
                },
            )

        except (ProgrammingError, OperationalError) as e:
            logger.debug(e)

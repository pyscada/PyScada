# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import logging

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.db.utils import ProgrammingError, OperationalError
from django.conf import settings


logger = logging.getLogger(__name__)

class PyScadaConfig(AppConfig):
    name = "pyscada"
    label = "pyscada"
    verbose_name = _("PyScada Core")
    path = os.path.dirname(os.path.realpath(__file__))
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import pyscada.signals
        from pyscada.core import additional_installed_app
        for app_name in additional_installed_app:
            if app_name not in settings.INSTALLED_APPS:
                logger.error(f"{app_name} missing in INSTALLED_APPS")


    def pyscada_app_init(self):
        logger.debug("Core init app")
        try:
            from .hmi.models import Theme

            if Theme.objects.filter().count():
                Theme.objects.first().check_all_themes()
        except (ProgrammingError, OperationalError) as e:
            logger.debug(e)

        try:
            from .models import DataSourceModel, DataSource
            from .django_datasource.models import DjangoDatabase
            from .cache_datasource.models import DjangoCache
            from .single_value_datasource.models import DjangoSingleValue

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
                    "data_model_app_name": "pyscada.django_datasource",
                    "data_model_name": "RecordedData",
                },
            )

            # For RecordedDataOld, hidden by default
            # set can_select to True to show it in the admin panel.
            # TODO : test read and write, test how it appears in the variable admin
            # panel config if mannualy added (using shell)
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
                id=2,
                defaults={
                    "datasource_model": dsm,
                },
            )
            dd, _ = DjangoDatabase.objects.get_or_create(
                datasource=ds,
                defaults={
                    "data_model_app_name": "pyscada.django_datasource",
                    "data_model_name": "RecordedDataOld",
                },
            )

            # Update datasource name after move to subapp
            DjangoDatabase.objects.filter(
                data_model_app_name="pyscada",
                pk__lte=2).update(data_model_app_name="pyscada.django_datasource")

            # Django Cache datastore
            dsm, _ = DataSourceModel.objects.get_or_create(
                inline_model_name="DjangoCache",
                name="Django Cache",
                defaults={
                    "can_add": True,
                    "can_change": True,
                    "can_select": True,
                },
            )
            ds, _ = DataSource.objects.get_or_create(
                datasource_model=dsm
                )
            dd, _ = DjangoCache.objects.get_or_create(
                datasource=ds,
                defaults={
                    "data_lifetime": 3600,
                },
            )

            # Django Single Value datastore
            dsm, _ = DataSourceModel.objects.get_or_create(
                inline_model_name="DjangoSingleValue",
                name="Django Single Value",
                defaults={
                    "can_add": False,
                    "can_change": False,
                    "can_select": True,
                },
            )
            ds, _ = DataSource.objects.get_or_create(
                datasource_model=dsm
                )
            dd, _ = DjangoSingleValue.objects.get_or_create(
                datasource=ds,
            )


        except (ProgrammingError, OperationalError) as e:
            logger.debug(e)

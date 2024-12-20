# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.db.utils import ProgrammingError, OperationalError
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


class PyScadaHMIConfig(AppConfig):
    name = "pyscada.hmi"
    verbose_name = _("PyScada HMI")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import pyscada.hmi.signals

    def pyscada_app_init(self):
        logger.debug("HMI init app")
        try:
            from .models import TransformData

            # create the control item transform data display value options
            # min, max, mean difference, difference percent...
            # TODO: do not get the whole historical data for first, difference, difference percent
            TransformData.objects.update_or_create(
                short_name="Min",
                defaults={
                    "inline_model_name": "TransformDataMin",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataMin",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="Max",
                defaults={
                    "inline_model_name": "TransformDataMax",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataMax",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="Total",
                defaults={
                    "inline_model_name": "TransformDataTotal",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataTotal",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="Difference",
                defaults={
                    "inline_model_name": "TransformDataDifference",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataDifference",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="DifferencePercent",
                defaults={
                    "inline_model_name": "TransformDataDifferencePercent",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataDifferencePercent",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="Delta",
                defaults={
                    "inline_model_name": "TransformDataDelta",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataDelta",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="Mean",
                defaults={
                    "inline_model_name": "TransformDataMean",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataMean",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="First",
                defaults={
                    "inline_model_name": "TransformDataFirst",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataFirst",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="Count",
                defaults={
                    "inline_model_name": "TransformDataCount",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataCount",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="CountValue",
                defaults={
                    "inline_model_name": "TransformDataCountValue",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataCountValue",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="Range",
                defaults={
                    "inline_model_name": "TransformDataRange",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataRange",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="Step",
                defaults={
                    "inline_model_name": "TransformDataStep",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataStep",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="ChangeCount",
                defaults={
                    "inline_model_name": "TransformDataChangeCount",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataChangeCount",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
            TransformData.objects.update_or_create(
                short_name="DistinctCount",
                defaults={
                    "inline_model_name": "TransformDataDistinctCount",
                    "js_function_name": "PyScadaControlItemDisplayValueTransformDataDistinctCount",
                    "js_files": "pyscada/js/pyscada/TransformDataHmiPlugin.js",
                    "need_historical_data": True,
                },
            )
        except (ProgrammingError, OperationalError) as e:
            logger.debug(e)

        try:
            from .models import DisplayValueOptionTemplate

            STATIC_URL = (
                str(settings.STATIC_URL)
                if hasattr(settings, "STATIC_URL")
                else "/static/"
            )

            # create the circular gauge for control item display value option
            DisplayValueOptionTemplate.objects.update_or_create(
                label="Circular gauge",
                defaults={
                    "template_name": "circular_gauge.html",
                    "js_files": "pyscada/js/jquery/jquery.tablesorter.min.js,"
                    + "pyscada/js/jquery/parser-input-select.js,"
                    + "pyscada/js/flot/lib/jquery.mousewheel.js,"
                    + "pyscada/js/flot/source/jquery.canvaswrapper.js,"
                    + "pyscada/js/flot/source/jquery.colorhelpers.js,"
                    + "pyscada/js/flot/source/jquery.flot.js,"
                    + "pyscada/js/flot/source/jquery.flot.saturated.js,"
                    + "pyscada/js/flot/source/jquery.flot.browser.js,"
                    + "pyscada/js/flot/source/jquery.flot.drawSeries.js,"
                    + "pyscada/js/flot/source/jquery.flot.errorbars.js,"
                    + "pyscada/js/flot/source/jquery.flot.uiConstants.js,"
                    + "pyscada/js/flot/source/jquery.flot.logaxis.js,"
                    + "pyscada/js/flot/source/jquery.flot.symbol.js,"
                    + "pyscada/js/flot/source/jquery.flot.flatdata.js,"
                    + "pyscada/js/flot/source/jquery.flot.navigate.js,"
                    + "pyscada/js/flot/source/jquery.flot.fillbetween.js,"
                    + "pyscada/js/flot/source/jquery.flot.stack.js,"
                    + "pyscada/js/flot/source/jquery.flot.touchNavigate.js,"
                    + "pyscada/js/flot/source/jquery.flot.hover.js,"
                    + "pyscada/js/flot/source/jquery.flot.touch.js,"
                    + "pyscada/js/flot/source/jquery.flot.time.js,"
                    + "pyscada/js/flot/source/jquery.flot.axislabels.js,"
                    + "pyscada/js/flot/source/jquery.flot.selection.js,"
                    + "pyscada/js/flot/source/jquery.flot.composeImages.js,"
                    + "pyscada/js/flot/source/jquery.flot.legend.js,"
                    + "pyscada/js/flot/source/jquery.flot.pie.js,"
                    + "pyscada/js/flot/source/jquery.flot.crosshair.js,"
                    + "pyscada/js/flot/source/jquery.flot.gauge.js,"
                    + "pyscada/js/jquery.flot.axisvalues.js",
                },
            )
        except (ProgrammingError, OperationalError) as e:
            logger.debug(e)

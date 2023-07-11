# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.admin import admin_site
from pyscada.export.models import ScheduledExportTask, ExportTask

from django.contrib import admin
import logging

logger = logging.getLogger(__name__)


class ScheduledExportTaskAdmin(admin.ModelAdmin):
    filter_horizontal = ("variables",)


class ExportTaskAdmin(admin.ModelAdmin):
    filter_horizontal = ("variables",)
    list_display = (
        "id",
        "label",
        "datetime_start",
        "datetime_finished",
        "mean_value_period",
        "file_format",
        "done",
        "busy",
        "failed",
        "downloadlink",
    )
    list_display_links = ("id", "label")
    readonly_fields = (
        "filename",
        "datetime_finished",
        "done",
        "busy",
        "failed",
        "backgroundprocess",
        "downloadlink",
    )
    save_as = True


admin_site.register(ScheduledExportTask, ScheduledExportTaskAdmin)
admin_site.register(ExportTask, ExportTaskAdmin)

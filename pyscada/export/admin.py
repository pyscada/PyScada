# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.admin import admin_site
from pyscada.export.models import ScheduledExportTask, ExportTask

from django.contrib import admin


class ScheduledExportTaskAdmin(admin.ModelAdmin):
    filter_horizontal = ('variables',)


class ExportTaskAdmin(admin.ModelAdmin):
    filter_horizontal = ('variables',)
    list_display = ('id', 'label', 'datetime_start', 'datetime_finished',
                    'mean_value_period', 'file_format', 'done', 'busy', 'failed',)
    readonly_fields = ('datetime_finished', 'done', 'busy', 'failed', 'backgroundprocess', 'downloadlink')

admin_site.register(ScheduledExportTask, ScheduledExportTaskAdmin)
admin_site.register(ExportTask, ExportTaskAdmin)

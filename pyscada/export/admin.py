# -*- coding: utf-8 -*-
from pyscada.admin import admin_site

from pyscada.export.models import ScheduledExportTask, ExportTask
from django import forms
from django.contrib import admin
from django import forms
from datetime import datetime
from time import mktime


class ScheduledExportTaskAdmin(admin.ModelAdmin):
    filter_horizontal = ('variables',)


class ExportTaskAdmin(admin.ModelAdmin):
    filter_horizontal = ('variables',)
    list_display = ('id','label','datetime_start','datetime_fineshed',\
        'mean_value_period','file_format','done','busy','failed',)
    readonly_fields = ('datetime_fineshed','done','busy','failed','backgroundtask','downloadlink')
   
admin_site.register(ScheduledExportTask,ScheduledExportTaskAdmin)
admin_site.register(ExportTask,ExportTaskAdmin)
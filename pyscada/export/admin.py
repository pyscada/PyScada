# -*- coding: utf-8 -*-
from pyscada.export.models import ScheduledExportTask, ExportTask
from django.contrib import admin
from django import forms
from datetime import datetime

class ScheduledExportTaskAdmin(admin.ModelAdmin):
    filter_horizontal = ('variables',)

class ExportTaskAdmin(admin.ModelAdmin):
    filter_horizontal = ('variables',)
    list_display = ('id','label','start_time','fineshed_time',\
        'mean_value_period','file_format','done','busy','failed',)
    
    def start_time(self,instance):
        if int(instance.start) == 0:
            return 'None'
        else:
            return datetime.fromtimestamp(int(instance.start)).strftime('%Y-%m-%d %H:%M:%S')
    def fineshed_time(self,instance):
        if int(instance.fineshed) == 0:
            return 'None'
        else:
            return datetime.fromtimestamp(int(instance.fineshed)).strftime('%Y-%m-%d %H:%M:%S')
    
admin.site.register(ScheduledExportTask,ScheduledExportTaskAdmin)
admin.site.register(ExportTask,ExportTaskAdmin)
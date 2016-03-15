# -*- coding: utf-8 -*-
from pyscada.export.models import ScheduledExportTask
from django.contrib import admin
from django import forms

class ScheduledExportTaskAdmin(admin.ModelAdmin):
    filter_horizontal = ('variables',)

admin.site.register(ScheduledExportTask,ScheduledExportTaskAdmin)
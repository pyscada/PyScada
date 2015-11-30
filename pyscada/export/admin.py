# -*- coding: utf-8 -*-
from pyscada.export.models import ExportJob
from django.contrib import admin
from django import forms

class ExportJobAdmin(admin.ModelAdmin):
    filter_horizontal = ('variables',)

admin.site.register(ExportJob,ExportJobAdmin)
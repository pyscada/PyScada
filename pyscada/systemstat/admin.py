# -*- coding: utf-8 -*-
from pyscada.admin import admin_site

from pyscada.systemstat.models import SystemStatVariable

from django.contrib import admin


class SystemStatVariableAdmin(admin.ModelAdmin):
    search_fields = ['system_stat_variable__name',]
    list_display = ('name','value_class','information',)
    raw_id_fields = ('system_stat_variable',)

    def name(self, instance):
        return instance.system_stat_variable.name

    def value_class(self, instance):
        return instance.system_stat_variable.value_class

admin_site.register(SystemStatVariable,SystemStatVariableAdmin)
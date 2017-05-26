# -*- coding: utf-8 -*-
from pyscada.admin import admin_site

from pyscada.onewire.models import OneWireVariable, OneWireDevice

from django.contrib import admin

class OneWireVariableAdmin(admin.ModelAdmin):
    list_display = ('name','value_class','address','sensor_type')
    raw_id_fields = ('onewire_variable',)
    def name(self, instance):
        return instance.onewire_variable.name
    def value_class(self, instance):
        return instance.onewire_variable.value_class

admin_site.register(OneWireVariable,OneWireVariableAdmin)
admin_site.register(OneWireDevice)
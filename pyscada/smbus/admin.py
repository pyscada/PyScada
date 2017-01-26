# -*- coding: utf-8 -*-
from pyscada.admin import admin_site

from pyscada.smbus.models import SMbusDevice
from pyscada.smbus.models import SMbusVariable

from django.contrib import admin

class SMbusDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name','description','port','address',)
    def device_name(self, instance):
        return instance.smbus_device.short_name
    def description(self, instance):
        return instance.smbus_device.description
        
class SMbusVariableAdmin(admin.ModelAdmin):
    search_fields = ['smbus_variable__name',]
    list_display = ('name','value_class','information',)
    raw_id_fields = ('smbus_variable',)
    def name(self, instance):
        return instance.smbus_variable.name
    def value_class(self, instance):
        return instance.smbus_variable.value_class

admin_site.register(SMbusDevice,SMbusDeviceAdmin)
admin_site.register(SMbusVariable,SMbusVariableAdmin)
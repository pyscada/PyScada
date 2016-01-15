# -*- coding: utf-8 -*-
from pyscada.modbus.models import ModbusDevice
from pyscada.modbus.models import ModbusVariable

from django.contrib import admin

class ModbusDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name','description','protocol','ip_address','port',)
    def device_name(self, instance):
        return instance.modbus_device.short_name
    def description(self, instance):
        return instance.modbus_device.description
        
class ModbusVariableAdmin(admin.ModelAdmin):
    search_fields = ['modbus_variable__name',]
    list_display = ('name','value_class','address',)
    raw_id_fields = ('modbus_variable',)
    def name(self, instance):
        return instance.modbus_variable.name
    def value_class(self, instance):
        return instance.modbus_variable.value_class

admin.site.register(ModbusDevice,ModbusDeviceAdmin)
admin.site.register(ModbusVariable,ModbusVariableAdmin)
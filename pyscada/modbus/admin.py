# -*- coding: utf-8 -*-
from pyscada.modbus.models import ClientModbusProperty
from pyscada.modbus.models import VariableModbusProperty

from django.contrib import admin

class ClientModbusPropertyAdmin(admin.ModelAdmin):
    list_display = ('client_name','description','protocol','ip_address','port',)
    def client_name(self, instance):
        return instance.modbus_client.short_name
    def description(self, instance):
        return instance.modbus_client.description
        
class VariableModbusPropertyAdmin(admin.ModelAdmin):
    search_fields = ['modbus_variable__variable_name',]
    list_display = ('variable_name','value_class','address',)
    def variable_name(self, instance):
        return instance.modbus_variable.variable_name
    def value_class(self, instance):
        return instance.modbus_variable.value_class

admin.site.register(ClientModbusProperty,ClientModbusPropertyAdmin)
admin.site.register(VariableModbusProperty,VariableModbusPropertyAdmin)
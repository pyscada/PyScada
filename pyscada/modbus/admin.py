# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.modbus import PROTOCOL_ID
from pyscada.modbus.models import ModbusDevice, ExtendedModbusDevice
from pyscada.modbus.models import ModbusVariable, ExtendedModbusVariable
from pyscada.admin import DeviceAdmin
from pyscada.admin import VariableAdmin
from pyscada.admin import admin_site
from pyscada.models import Device, DeviceProtocol
from django.contrib import admin
import logging

logger = logging.getLogger(__name__)


class ModbusDeviceAdminInline(admin.StackedInline):
    model = ModbusDevice


class ModbusDeviceAdmin(DeviceAdmin):
    list_display = ('id', 'short_name', 'description', 'protocol', 'active', 'polling_interval', 'protocol_modbus', 'framer', 'ip_address', 'port', 'unit_id')

    def protocol_modbus(self, instance):
        return instance.modbusdevice.protocol_choices[instance.modbusdevice.protocol][1]

    def framer(self, instance):
        try:
            return instance.modbusdevice.framer_choices[instance.modbusdevice.framer][1]
        except TypeError:
            return ""

    def ip_address(self, instance):
        return instance.modbusdevice.ip_address

    def port(self, instance):
        return instance.modbusdevice.port

    def unit_id(self, instance):
        return instance.modbusdevice.unit_id

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'protocol':
            kwargs['queryset'] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(ModbusDeviceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(ModbusDeviceAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)

    inlines = [
        ModbusDeviceAdminInline
    ]


class ModbusVariableAdminInline(admin.StackedInline):
    model = ModbusVariable


class ModbusVariableAdmin(VariableAdmin):
    list_display = ('id', 'name', 'description', 'unit', 'scaling', 'device_name', 'value_class', 'active', 'writeable', 'address',
                    'function_code_read',)
    list_editable = ('active', 'writeable',)
    list_display_links = ('name',)

    def address(self, instance):
        return instance.modbusvariable.address

    def function_code_read(self, instance):
        return instance.modbusvariable.function_code_read

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'device':
            kwargs['queryset'] = Device.objects.filter(protocol=PROTOCOL_ID)
        return super(ModbusVariableAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(ModbusVariableAdmin, self).get_queryset(request)
        return qs.filter(device__protocol_id=PROTOCOL_ID)

    inlines = [
        ModbusVariableAdminInline
    ]


admin_site.register(ExtendedModbusDevice, ModbusDeviceAdmin)
admin_site.register(ExtendedModbusVariable, ModbusVariableAdmin)

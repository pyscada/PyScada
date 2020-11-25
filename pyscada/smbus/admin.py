# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.admin import admin_site
from pyscada.admin import DeviceAdmin
from pyscada.admin import CoreVariableAdmin
from pyscada.models import Device, DeviceProtocol

from pyscada.smbus import PROTOCOL_ID
from pyscada.smbus.models import SMBusDevice, SMBusDeviceHandler
from pyscada.smbus.models import SMBusVariable, ExtendedSMBusDevice, ExtendedSMBusVariable

from django.contrib import admin
import logging

logger = logging.getLogger(__name__)


class SMBusDeviceAdminInline(admin.StackedInline):
    model = SMBusDevice


class SMBusDeviceAdmin(DeviceAdmin):
    list_display = DeviceAdmin.list_display + ('instrument', 'port', 'address',)

    def address(self, instance):
        try:
            for choice in instance.smbusdevice.address_choices:
                if choice[0] == instance.smbusdevice.address:
                    return choice[1]
            return ""
        except TypeError:
            return ""

    def instrument(self, instance):
        return instance.smbusdevice.instrument

    def port(self, instance):
        return instance.smbusdevice.port

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'protocol':
            kwargs['queryset'] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(SMBusDeviceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(SMBusDeviceAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)

    inlines = [
        SMBusDeviceAdminInline
    ]


class SMBusVariableAdminInline(admin.StackedInline):
    model = SMBusVariable


class SMBusVariableAdmin(CoreVariableAdmin):
    list_display = CoreVariableAdmin.list_display + ('information',)

    def information(self, instance):
        return instance.smbusvariable.information

    def name(self, instance):
        return instance.smbus_variable.name

    def value_class(self, instance):
        return instance.smbus_variable.value_class

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'device':
            kwargs['queryset'] = Device.objects.filter(protocol=PROTOCOL_ID)
        return super(SMBusVariableAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(SMBusVariableAdmin, self).get_queryset(request)
        return qs.filter(device__protocol_id=PROTOCOL_ID)

    inlines = [
        SMBusVariableAdminInline
    ]


admin_site.register(ExtendedSMBusDevice, SMBusDeviceAdmin)
admin_site.register(ExtendedSMBusVariable, SMBusVariableAdmin)
admin_site.register(SMBusDeviceHandler)

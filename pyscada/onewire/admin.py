# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.admin import admin_site
from pyscada.models import Device, DeviceProtocol

from pyscada.onewire import PROTOCOL_ID
from pyscada.onewire.models import OneWireVariable, OneWireDevice, ExtendedOneWireDevice, ExtendedOneWireVariable
from pyscada.admin import DeviceAdmin
from pyscada.admin import CoreVariableAdmin
from django.contrib import admin
import logging

logger = logging.getLogger(__name__)



class OneWireDeviceAdminInline(admin.StackedInline):
    model = OneWireDevice


class OneWireDeviceAdmin(DeviceAdmin):
    list_display = DeviceAdmin.list_display + ('adapter_type', 'config',)

    def adapter_type(self, instance):
        try:
            for choice in instance.onewiredevice.adapter_type_choices:
                if choice[0] == instance.onewiredevice.adapter_type:
                    return choice[1]
            return ""
        except TypeError:
            return ""

    def config(self, instance):
        return instance.onewiredevice.config

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'protocol':
            kwargs['queryset'] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(OneWireDeviceAdmin,self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(OneWireDeviceAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)

    inlines = [
        OneWireDeviceAdminInline
    ]


class OneWireVariableAdminInline(admin.StackedInline):
    model = OneWireVariable


class OneWireVariableAdmin(CoreVariableAdmin):
    list_display = CoreVariableAdmin.list_display + ('address', 'sensor_type',)

    def address(self, instance):
        return instance.onewirevariable.address

    def sensor_type(self, instance):
        try:
            for choice in instance.onewirevariable.sensor_type_choices:
                if choice[0] == instance.onewirevariable.sensor_type:
                    return choice[1]
            return ""
        except TypeError:
            return ""

    def name(self, instance):
        return instance.onewire_variable.name

    def value_class(self, instance):
        return instance.onewire_variable.value_class

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'device':
            kwargs['queryset'] = Device.objects.filter(protocol=PROTOCOL_ID)
        return super(OneWireVariableAdmin,self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(OneWireVariableAdmin, self).get_queryset(request)
        return qs.filter(device__protocol_id=PROTOCOL_ID)

    inlines = [
        OneWireVariableAdminInline
    ]


# admin_site.register(ExtendedOneWireVariable, OneWireVariableAdmin)
# admin_site.register(ExtendedOneWireDevice,OneWireDeviceAdmin)

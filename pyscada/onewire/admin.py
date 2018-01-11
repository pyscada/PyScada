# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.admin import admin_site
from pyscada.models import Device, DeviceProtocol
from pyscada.models import Variable

from pyscada.onewire import PROTOCOL_ID
from pyscada.onewire.models import OneWireVariable, OneWireDevice
from pyscada.admin import DeviceAdmin
from pyscada.admin import VariableAdmin
from django.contrib import admin
import logging

logger = logging.getLogger(__name__)


class ExtendedOneWireDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'OneWire Device'
        verbose_name_plural = 'OneWire Devices'


class OneWireDeviceAdminInline(admin.StackedInline):
    model = OneWireDevice


class OneWireDeviceAdmin(DeviceAdmin):
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


class ExtendedOneWireVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'OneWire Variable'
        verbose_name_plural = 'OneWire Variable'


class OneWireVariableAdminInline(admin.StackedInline):
    model = OneWireVariable


class OneWireVariableAdmin(VariableAdmin):
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

admin_site.register(ExtendedOneWireVariable, OneWireVariableAdmin)
admin_site.register(ExtendedOneWireDevice,OneWireDeviceAdmin)

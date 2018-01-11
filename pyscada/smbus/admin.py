# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.admin import admin_site
from pyscada.admin import DeviceAdmin
from pyscada.admin import VariableAdmin
from pyscada.models import Variable
from pyscada.models import Device, DeviceProtocol

from pyscada.smbus import PROTOCOL_ID
from pyscada.smbus.models import SMbusDevice
from pyscada.smbus.models import SMbusVariable

from django.contrib import admin
import logging

logger = logging.getLogger(__name__)


class ExtendedSMBusDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'SMBus Device'
        verbose_name_plural = 'SMBus Devices'


class SMbusDeviceAdminInline(admin.StackedInline):
    model = SMbusDevice


class SMbusDeviceAdmin(DeviceAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'protocol':
            kwargs['queryset'] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(SMbusDeviceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(SMbusDeviceAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)

    inlines = [
        SMbusDeviceAdminInline
    ]


class ExtendedSMbusVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'SMBus Variable'
        verbose_name_plural = 'SMBus Variables'


class SMbusVariableAdminInline(admin.StackedInline):
    model = SMbusVariable


class SMbusVariableAdmin(VariableAdmin):
    def name(self, instance):
        return instance.smbus_variable.name

    def value_class(self, instance):
        return instance.smbus_variable.value_class

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'device':
            kwargs['queryset'] = Device.objects.filter(protocol=PROTOCOL_ID)
        return super(SMbusVariableAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(SMbusVariableAdmin, self).get_queryset(request)
        return qs.filter(device__protocol_id=PROTOCOL_ID)

    inlines = [
        SMbusVariableAdminInline
    ]

admin_site.register(ExtendedSMBusDevice, SMbusDeviceAdmin)
admin_site.register(ExtendedSMbusVariable, SMbusVariableAdmin)

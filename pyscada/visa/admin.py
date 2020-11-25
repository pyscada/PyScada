# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.visa import PROTOCOL_ID
from pyscada.visa.models import VISAVariable
from pyscada.visa.models import VISADevice
from pyscada.visa.models import VISADeviceHandler, ExtendedVISADevice, ExtendedVISAVariable
from pyscada.admin import DeviceAdmin
from pyscada.admin import CoreVariableAdmin
from pyscada.admin import admin_site
from pyscada.models import Device, DeviceProtocol

from django.contrib import admin
import logging

logger = logging.getLogger(__name__)


class DeviceAdminInline(admin.StackedInline):
    model = VISADevice


class VISADeviceAdmin(DeviceAdmin):
    list_display = DeviceAdmin.list_display + ('resource_name', 'instrument',)

    def resource_name(self, instance):
        return instance.visadevice.resource_name

    def instrument(self, instance):
        return instance.visadevice.instrument

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'protocol':
            kwargs['queryset'] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(VISADeviceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(VISADeviceAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)

    inlines = [
        DeviceAdminInline
    ]


class VISAVariableAdminInline(admin.StackedInline):
    model = VISAVariable


class VISAVariableAdmin(CoreVariableAdmin):
    list_display = CoreVariableAdmin.list_display + ('device_property', 'variable_type',)

    def device_property(self, instance):
        return instance.visavariable.device_property

    def variable_type(self, instance):
        try:
            for choice in instance.visavariable.variable_type_choices:
                if choice[0] == instance.visavariable.variable_type:
                    return choice[1]
            return ""
        except TypeError:
            return ""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'device':
            kwargs['queryset'] = Device.objects.filter(protocol=PROTOCOL_ID)
        return super(VISAVariableAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(VISAVariableAdmin, self).get_queryset(request)
        return qs.filter(device__protocol_id=PROTOCOL_ID)

    inlines = [
        VISAVariableAdminInline
    ]


admin_site.register(ExtendedVISADevice, VISADeviceAdmin)
admin_site.register(ExtendedVISAVariable, VISAVariableAdmin)
admin_site.register(VISADeviceHandler)

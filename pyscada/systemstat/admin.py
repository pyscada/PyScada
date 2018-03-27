# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.systemstat.models import SystemStatVariable, ExtendedSystemStatDevice, ExtendedSystemStatVariable
from pyscada.systemstat import PROTOCOL_ID
from pyscada.admin import admin_site
from pyscada.admin import DeviceAdmin
from pyscada.admin import VariableAdmin
from pyscada.models import Device, DeviceProtocol

from django.contrib import admin
import logging

logger = logging.getLogger(__name__)


class SystemStatDeviceAdmin(DeviceAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'protocol':
            kwargs['queryset'] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(SystemStatDeviceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(SystemStatDeviceAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)


class SystemStatVariableAdminInline(admin.StackedInline):
    model = SystemStatVariable


class SystemStatVariableAdmin(VariableAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'device':
            kwargs['queryset'] = Device.objects.filter(protocol=PROTOCOL_ID)
        return super(SystemStatVariableAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(SystemStatVariableAdmin, self).get_queryset(request)
        return qs.filter(device__protocol_id=PROTOCOL_ID)

    inlines = [
        SystemStatVariableAdminInline
    ]

admin_site.register(ExtendedSystemStatDevice, SystemStatDeviceAdmin)
admin_site.register(ExtendedSystemStatVariable, SystemStatVariableAdmin)

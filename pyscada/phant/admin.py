# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.admin import admin_site
from pyscada.admin import DeviceAdmin
from pyscada.admin import VariableAdmin
from pyscada.models import Device, DeviceProtocol

from pyscada.phant import PROTOCOL_ID
from pyscada.phant.models import PhantDevice, ExtendedPhantVariable, ExtendedPhantDevice

from django.contrib import admin
import logging

logger = logging.getLogger(__name__)


class PhantDeviceAdminInline(admin.StackedInline):
    model = PhantDevice


class PhantDeviceAdmin(DeviceAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'protocol':
            kwargs['queryset'] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(PhantDeviceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(PhantDeviceAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)
    
    inlines = [
        PhantDeviceAdminInline
    ]

class PhantVariableAdmin(VariableAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'device':
            kwargs['queryset'] = Device.objects.filter(protocol=PROTOCOL_ID)
        return super(PhantVariableAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(PhantVariableAdmin, self).get_queryset(request)
        return qs.filter(device__protocol_id=PROTOCOL_ID)


admin_site.register(ExtendedPhantDevice, PhantDeviceAdmin)
admin_site.register(ExtendedPhantVariable, PhantVariableAdmin)

# -*- coding: utf-8 -*-
from pyscada.admin import admin_site

from pyscada.onewire.models import OneWireVariable

from django.contrib import admin


admin_site.register(OneWireVariable)
# -*- coding: utf-8 -*-
from pyscada.admin import admin_site

from pyscada.visa.models import *

from django.contrib import admin


admin_site.register(VISAVariable)
admin_site.register(VISADevice)
admin_site.register(VISADeviceHandler)

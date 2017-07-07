# -*- coding: utf-8 -*-
from pyscada.admin import admin_site

from pyscada.visa.models import *


admin_site.register(VISAVariable)
admin_site.register(VISADevice)
admin_site.register(VISADeviceHandler)

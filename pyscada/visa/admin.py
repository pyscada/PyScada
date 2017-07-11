# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.admin import admin_site

from pyscada.visa.models import *


admin_site.register(VISAVariable)
admin_site.register(VISADevice)
admin_site.register(VISADeviceHandler)

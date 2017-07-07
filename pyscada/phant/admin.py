# -*- coding: utf-8 -*-
from pyscada.admin import admin_site

from pyscada.phant.models import PhantDevice


admin_site.register(PhantDevice)
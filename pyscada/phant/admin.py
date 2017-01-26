# -*- coding: utf-8 -*-
from pyscada.admin import admin_site

from pyscada.phant.models import PhantDevice

from django.contrib import admin


admin_site.register(PhantDevice)
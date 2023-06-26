# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
import logging

logger = logging.getLogger(__name__)

urlpatterns = []

for app in apps.app_configs.values():
    if app.name.startswith('pyscada.') and app.name != "pyscada.core":
        
        try:
            m = __import__(f"{app.name}.urls", fromlist=[str('a')])
            urlpatterns += m.urlpatterns
        
        except Exception as e:
            logger.warning(e, exc_info=True)


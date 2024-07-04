# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
import logging

logger = logging.getLogger(__name__)

urlpatterns = []

for app_config in apps.get_app_configs():
    if app_config.name.startswith("pyscada.") and app_config.name != "pyscada.core":
        try:
            m = __import__(f"{app_config.name}.urls", fromlist=[str("a")])
            urlpatterns += m.urlpatterns
        except ModuleNotFoundError:
            pass
        except Exception as e:
            logger.warning(e, exc_info=True)

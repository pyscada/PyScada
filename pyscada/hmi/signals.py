# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

import logging

logger = logging.getLogger(__name__)

# moved to hmi.models.WidgetContentModel.__init_subclass__

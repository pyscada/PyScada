# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.hmi.models import WidgetContent, WidgetContentModel

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

import logging

logger = logging.getLogger(__name__)


@receiver(pre_delete)
def _delete_widget_content(sender, instance, **kwargs):
    """
    delete the widget content instance when a WidgetContentModel is deleted
    """
    if not issubclass(sender, WidgetContentModel):
        return

    # delete WidgetContent Entry
    wcs = WidgetContent.objects.filter(
        content_pk=instance.pk,
        content_model=('%s' % instance.__class__).replace("<class '", '').replace("'>", ''))
    for wc in wcs:
        logger.debug('delete wc %r'%wc)
        wc.delete()


@receiver(post_save)
def _create_widget_content(sender, instance, created=False, **kwargs):
    """
    create a widget content instance when a WidgetContentModel is deleted
    """
    if not issubclass(sender, WidgetContentModel):
        return

    # create a WidgetContent Entry
    if created:
        instance.create_widget_content_entry()
    else:
        instance.update_widget_content_entry()
    return

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import gc
from datetime import datetime
from time import time
from pytz import UTC
import logging

logger = logging.getLogger(__name__)


def queryset_iterator(queryset, chunk_size=100000):
    counter = 0
    count = chunk_size
    while count == chunk_size:
        offset = counter - counter % chunk_size
        count = 0
        for item in queryset.all()[offset:offset + chunk_size]:
            count += 1
            yield item
        counter += count
        gc.collect()


def move_recorded_data(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    RecordedDataNew = apps.get_model("pyscada", "RecordedDataNew")
    RecordedData = apps.get_model("pyscada", "RecordedData")

    recoded_data_set = queryset_iterator(RecordedData.objects.using(schema_editor.connection.alias).all().order_by('-pk'))
    count = 0
    count_all = 0
    timeout = time() + 60 * 5
    items = []
    for item in recoded_data_set:
        items.append(RecordedDataNew(id=item.id,
                                     variable_id=item.variable_id,
                                     value_boolean=item.value_boolean,
                                     value_int16=item.value_int16,
                                     value_int32=item.value_int32,
                                     value_int64=item.value_int64,
                                     value_float64=item.value_float64,
                                     date_saved=datetime.fromtimestamp((item.pk - item.variable.pk) / 2097152 / 1000.0,
                                                                       UTC)
                                     ))
        if time() > timeout:
            break

        count += 1
        if count >= 10000:
            RecordedDataNew.objects.bulk_create(items)
            items = []
            count_all += count
            count = 0
            logger.info('wrote %d lines in total\n'%count_all)

    if len(items) > 0:
        RecordedDataNew.objects.bulk_create(items)
        count_all += len(items)
        logger.info('wrote %d lines in total\n' % count_all)


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0047_recordeddatanew'),
    ]

    operations = [
        migrations.RunPython(move_recorded_data),
    ]
# -*- coding: utf-8 -*-
"""
copies data from pyscada.models.RecordedDataOld to RecordedData
the script will terminate after 5 minutes, if you would like to copy more content change the timeout accordingly
"""

from __future__ import unicode_literals

from pyscada.models import RecordedData, RecordedDataOld
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


if __name__ == '__main__':

    recoded_data_set = queryset_iterator(RecordedDataOld.objects.filter(pk__lt=RecordedData.objects.first().pk))

    count = 0
    count_all = 0
    timeout = time() + 60 * 5 # <-- set the timeout in minutes
    items = []
    for item in recoded_data_set:
        items.append(RecordedData(id=item.id,
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
            RecordedData.objects.bulk_create(items)
            items = []
            count_all += count
            count = 0
            logger.info('wrote %d lines in total\n'%count_all)

    if len(items) > 0:
        RecordedData.objects.bulk_create(items)
        count_all += len(items)
        logger.info('wrote %d lines in total\n' % count_all)

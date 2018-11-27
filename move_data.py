# -*- coding: utf-8 -*-
"""
copies data from pyscada.models.RecordedDataOld to RecordedData
the script will terminate after 5 minutes, if you would like to copy more content change the timeout accordingly
"""

from __future__ import unicode_literals
import os

import gc
from datetime import datetime
from time import time
from pytz import UTC
import logging

logger = logging.getLogger('pyscada.core.move_data')


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
    os.chdir('/var/www/pyscada/PyScadaServer')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PyScadaServer.settings")
    import django

    django.setup()
    from pyscada.models import RecordedData, RecordedDataOld
    min_pk = RecordedData.objects.first().pk
    recoded_data_set = queryset_iterator(RecordedDataOld.objects.filter(pk__lt=min_pk).order_by('-pk'))
    #recoded_data_set = queryset_iterator(RecordedDataOld.objects.all().order_by('-pk'))
    #logger.info('%d'%min_pk)
    #logger.info('%d'%RecordedDataOld.objects.filter(pk__lt=min_pk).count())
    count = 0
    count_all = 0
    timeout = time() + 60 * 10  # <-- set the timeout in minutes
    items = []
    for item in recoded_data_set:
        #if RecordedData.objects.filter(pk=item.id):
        #    continue
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
            logger.info('wrote %d lines in total\n' % count_all)

    if len(items) > 0:
        RecordedData.objects.bulk_create(items)
        count_all += len(items)
        logger.info('wrote %d lines in total\n' % count_all)

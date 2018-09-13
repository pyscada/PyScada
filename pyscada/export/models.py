# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, BackgroundProcess

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

import os
import time
from datetime import datetime
from pytz import UTC
import logging

logger = logging.getLogger(__name__)

#
# Model
#


def datetime_now():
    return datetime.now(UTC)


@python_2_unicode_compatible
class ScheduledExportTask(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=400, default='')
    variables = models.ManyToManyField(Variable)
    day_time_choices = [(x, '%d:00' % x) for x in range(0, 24)]
    day_time = models.PositiveSmallIntegerField(default=0, choices=day_time_choices,
                                                help_text='day time wenn the job will be started in UTC')
    mean_value_period = models.PositiveSmallIntegerField(default=0, help_text='in Seconds (0 = no mean value)')
    active = models.BooleanField(default=False, blank=True, help_text='to activate scheduled export')
    file_format_choices = (('hdf5', 'Hierarchical Data Format Version 5'),
                           ('mat', 'Matlab® mat v7.3 compatible file'),
                           ('CSV_EXCEL', 'Microsoft® Excel® compatible csv file'))
    file_format = models.CharField(max_length=400, default='hdf5', choices=file_format_choices)
    export_period_choices = ((1, '1 Day'),
                             (2, '2 Days (on every even Day of the year)'),
                             (7, '7 Days (on Mondays)'),
                             (14, '14 Days'),
                             (30, '30 Days'))
    export_period = models.PositiveSmallIntegerField(default=0, choices=export_period_choices, help_text='')

    def __str__(self):
        return self.label


@python_2_unicode_compatible
class ExportTask(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=400, default='None', blank=True)
    backgroundprocess = models.ForeignKey(BackgroundProcess, null=True, blank=True, on_delete=models.SET_NULL)
    variables = models.ManyToManyField(Variable)
    mean_value_period = models.PositiveSmallIntegerField(default=0, help_text='in Seconds (0 = no mean value)')
    file_format_choices = (('hdf5', 'Hierarchical Data Format Version 5'), ('mat', 'Matlab® mat v7.3 compatible file'),
                           ('CSV_EXCEL', 'Microsoft® Excel® compatible csv file'))
    file_format = models.CharField(max_length=400, default='hdf5', choices=file_format_choices)
    filename_suffix = models.CharField(max_length=400, default='', blank=True)
    datetime_min = models.DateTimeField(default=None, null=True)
    datetime_max = models.DateTimeField(default=None, null=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    datetime_start = models.DateTimeField(default=datetime_now)
    datetime_finished = models.DateTimeField(null=True, blank=True)
    done = models.BooleanField(default=False, blank=True)  # label task has been done
    busy = models.BooleanField(default=False, blank=True)  # label task is in operation done
    failed = models.BooleanField(default=False, blank=True)  # label task has failed
    filename = models.CharField(blank=True, null=True, max_length=1000)

    def __str__(self):
        return self.label

    def time_min(self):
        return time.mktime(self.datetime_min.timetuple())

    def time_max(self):
        return time.mktime(self.datetime_max.timetuple())

    def start(self):
        return time.mktime(self.datetime_start.timetuple())

    def finished(self):
        return time.mktime(self.datetime_finished.timetuple())

    def downloadlink(self):
        if not self.done:
            return 'busy...'
        backup_file_path = os.path.expanduser('~/measurement_data_dumps')
        if hasattr(settings, 'PYSCADA_EXPORT'):
            if 'output_folder' in settings.PYSCADA_EXPORT:
                backup_file_path = os.path.expanduser(settings.PYSCADA_EXPORT['output_folder'])
        return '<a href="%s">%s</a>' % (self.filename.replace(backup_file_path, '/measurement'),
                                        self.filename.replace(backup_file_path, '/measurement'))

    downloadlink.allow_tags = True

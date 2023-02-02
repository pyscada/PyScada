# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, Device
from . import PROTOCOL_ID

from django.db import models
import datetime
import logging

logger = logging.getLogger(__name__)


class SystemStatVariable(models.Model):
    system_stat_variable = models.OneToOneField(Variable, on_delete=models.CASCADE)
    information_choices = (
        (0, 'cpu_percent'),
        (1, 'virtual_memory_usage_total'),
        (2, 'virtual_memory_usage_available'),
        (3, 'virtual_memory_usage_percent'),
        (4, 'virtual_memory_usage_used'),
        (5, 'virtual_memory_usage_free'),
        (6, 'virtual_memory_usage_active'),
        (7, 'virtual_memory_usage_inactive'),
        (8, 'virtual_memory_usage_buffers'),
        (9, 'virtual_memory_usage_cached'),
        (10, 'swap_memory_total'),
        (11, 'swap_memory_used'),
        (12, 'swap_memory_free'),
        (13, 'swap_memory_percent'),
        (14, 'swap_memory_sin'),
        (15, 'swap_memory_sout'),
        (17, 'disk_usage_systemdisk_percent'),
        (18, 'disk_usage_percent'),
        (19, 'network_ip_address'),
        (100, 'APCUPSD Online Status (True/False)'),
        (101, 'APCUPSD Line Voltage'),  # Volts
        (102, 'APCUPSD Battery Voltage'),  # Volts
        (103, 'APCUPSD Battery Charge in %'),  # %
        (104, 'APCUPSD Battery Time Left in Minutes'),  # Minutes
        (105, 'APCUPSD Load in %'),  # %
        (200, 'List first X/last X/all items of a directory'),
        (201, 'List first X/last X/all items of a ftp directory'),
        (300, 'timestamp (UTC). Use parameter to set offset.'),
    )
    information = models.PositiveSmallIntegerField(choices=information_choices,
                                                   help_text="For item list create a VP for each path.")
    parameter = models.CharField(default='', max_length=400, blank=True, null=True,
                                 help_text="For 'disk_usage' insert the path.<br>"
                                           "For 'timestamp' define an offset in seconds (positive means in the future)"
                                           "(accept a decimal number up to the millisecond).<br>"
                                           "For 'network_ip_address' specify the interface name.<br>"
                                           "Examples for items list (local) : first 10 / last 5 / all.<br>"
                                           "Examples for items list (ftp) : "
                                           "127.0.0.1 first 10 / "
                                           "ftp.test.com last 5 / "
                                           "192.168.1.5 all.<br>")

    protocol_id = PROTOCOL_ID

    def __str__(self):
        return self.system_stat_variable.name

    def query_prev_value(self, time_min=None):
        print('ok')
        if self.information == 300:
            print('300')
            value = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
            try:
                value += datetime.timedelta(seconds=int(self.parameter),
                                            milliseconds=int((float(self.parameter) - int(self.parameter)) * 1000))
            except (ValueError, TypeError):
                pass
            self.system_stat_variable.prev_value = value.timestamp()
            self.system_stat_variable.timestamp_old = datetime.datetime.now().timestamp()
            print(self.system_stat_variable.prev_value)
            return True

        return self.system_stat_variable.query_prev_value(time_min, False)


class ExtendedSystemStatDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'SystemStat Device'
        verbose_name_plural = 'SystemStat Devices'


class ExtendedSystemStatVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'SystemStat Variable'
        verbose_name_plural = 'SystemStat Variables'

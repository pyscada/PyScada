# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, Device

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
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
    )
    information = models.PositiveSmallIntegerField(choices=information_choices,
                                                   help_text="For 'network_ip_address' create a variable property "
                                                             "attached to this variable with the interface in the name "
                                                             "of the VP")
    parameter = models.CharField(default='', max_length=400, blank=True, null=True,
                                 help_text="For 'disk_usage' insert the path")

    def __str__(self):
        return self.system_stat_variable.name


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

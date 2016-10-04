# -*- coding: utf-8 -*-
from pyscada.models import Variable
from pyscada.models import BackgroundTask

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from time import time


class SystemStatVariable(models.Model):
    system_stat_variable = models.OneToOneField(Variable)
    information_choices 	= (
        (0,'cpu_percent'),
        (1,'virtual_memory_usage_total'),
        (2,'virtual_memory_usage_available'),
        (3,'virtual_memory_usage_percent'),
        (4,'virtual_memory_usage_used'),
        (5,'virtual_memory_usage_free'),
        (6,'virtual_memory_usage_active'),
        (7,'virtual_memory_usage_inactive'),
        (8,'virtual_memory_usage_buffers'),
        (9,'virtual_memory_usage_cached'),
        (10,'swap_memory_total'),
        (11,'swap_memory_used'),
        (12,'swap_memory_free'),
        (13,'swap_memory_percent'),
        (14,'swap_memory_sin'),
        (15,'swap_memory_sout'),
        (17,'disk_usage_systemdisk_percent'),
        (18,'disk_usage_percent'),
        (100, 'APCUPSD Online Status (True/False)'),
        (101, 'APCUPSD Line Voltage'), # Volts
        (102, 'APCUPSD Battery Voltage'), # Volts
        (103, 'APCUPSD Battery Charge in %'), # %
        (104, 'APCUPSD Battery Time Left in Minutes'), # Minutes
        (105, 'APCUPSD Load in %'), # %
    )
    information	= models.PositiveSmallIntegerField(default=0,choices=information_choices)
    parameter   = models.CharField(default='',max_length=400,blank=True,null=True)
    def __unicode__(self):
        return unicode(self.system_stat_variable.name)
        
@receiver(post_save, sender=SystemStatVariable)
def _reinit_daq_daemons(sender, **kwargs):
    """
    update the daq daemon configuration wenn changes be applied in the models
    """
    BackgroundTask.objects.filter(label='pyscada.daq.daemon',done=0,failed=0).update(message='reinit',restart_daemon=True,timestamp = time())
# -*- coding: utf-8 -*-
from pyscada.models import Client as Client
from pyscada.models import Variable as Variable


from django.db import models


class SystemStatVariable(models.Model):
    system_stat_variable = models.OneToOneField(Variable)
    information_choices 	= (
        (0,'cpu_percent'),
        (1,'phymem_usage_total'),
        (2,'phymem_usage_available'),
        (3,'phymem_usage_percent'),
        (4,'phymem_usage_used'),
        (5,'phymem_usage_free'),
        (6,'phymem_usage_active'),
        (7,'phymem_usage_inactive'),
        (8,'phymem_usage_buffers'),
        (9,'phymem_usage_cached'),
        (10,'swap_memory_total'),
        (11,'swap_memory_used'),
        (12,'swap_memory_free'),
        (13,'swap_memory_percent'),
        (14,'swap_memory_sin'),
        (15,'swap_memory_sout'),
        (16,'cached_phymem'),
        (17,'disk_usage_systemdisk'),
        (18,'disk_usage'),
    )
    information	= models.PositiveSmallIntegerField(default=0,choices=information_choices)
    parameter   = models.CharField(default='',max_length=400,blank=True,null=True)
    
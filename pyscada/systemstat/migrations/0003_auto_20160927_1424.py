# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systemstat', '0002_auto_20160115_0918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemstatvariable',
            name='information',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'cpu_percent'), (1, 'virtual_memory_usage_total'), (2, 'virtual_memory_usage_available'), (3, 'virtual_memory_usage_percent'), (4, 'virtual_memory_usage_used'), (5, 'virtual_memory_usage_free'), (6, 'virtual_memory_usage_active'), (7, 'virtual_memory_usage_inactive'), (8, 'virtual_memory_usage_buffers'), (9, 'virtual_memory_usage_cached'), (10, 'swap_memory_total'), (11, 'swap_memory_used'), (12, 'swap_memory_free'), (13, 'swap_memory_percent'), (14, 'swap_memory_sin'), (15, 'swap_memory_sout'), (17, 'disk_usage_systemdisk_percent'), (18, 'disk_usage_percent'), (100, 'APCUPSD Online Status (True/False)'), (101, 'APCUPSD Line Voltage'), (102, 'APCUPSD Battery Voltage'), (103, 'APCUPSD Battery Charge in %'), (104, 'APCUPSD Battery Time Left in Minutes'), (105, 'APCUPSD Load in %')]),
        ),
    ]

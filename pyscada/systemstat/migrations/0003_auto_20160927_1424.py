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
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'cpu_percent'), (1, b'virtual_memory_usage_total'), (2, b'virtual_memory_usage_available'), (3, b'virtual_memory_usage_percent'), (4, b'virtual_memory_usage_used'), (5, b'virtual_memory_usage_free'), (6, b'virtual_memory_usage_active'), (7, b'virtual_memory_usage_inactive'), (8, b'virtual_memory_usage_buffers'), (9, b'virtual_memory_usage_cached'), (10, b'swap_memory_total'), (11, b'swap_memory_used'), (12, b'swap_memory_free'), (13, b'swap_memory_percent'), (14, b'swap_memory_sin'), (15, b'swap_memory_sout'), (17, b'disk_usage_systemdisk_percent'), (18, b'disk_usage_percent'), (100, b'APCUPSD Online Status (True/False)'), (101, b'APCUPSD Line Voltage'), (102, b'APCUPSD Battery Voltage'), (103, b'APCUPSD Battery Charge in %'), (104, b'APCUPSD Battery Time Left in Minutes'), (105, b'APCUPSD Load in %')]),
        ),
    ]

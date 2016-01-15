# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systemstat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemstatvariable',
            name='information',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'cpu_percent'), (1, b'virtual_memory_usage_total'), (2, b'virtual_memory_usage_available'), (3, b'virtual_memory_usage_percent'), (4, b'virtual_memory_usage_used'), (5, b'virtual_memory_usage_free'), (6, b'virtual_memory_usage_active'), (7, b'virtual_memory_usage_inactive'), (8, b'virtual_memory_usage_buffers'), (9, b'virtual_memory_usage_cached'), (10, b'swap_memory_total'), (11, b'swap_memory_used'), (12, b'swap_memory_free'), (13, b'swap_memory_percent'), (14, b'swap_memory_sin'), (15, b'swap_memory_sout'), (17, b'disk_usage_systemdisk_percent'), (18, b'disk_usage_percent')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0006_auto_20151130_1449'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemStatVariable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('information', models.PositiveSmallIntegerField(default=0, choices=[(0, b'cpu_percent'), (1, b'phymem_usage_total'), (2, b'phymem_usage_available'), (3, b'phymem_usage_percent'), (4, b'phymem_usage_used'), (5, b'phymem_usage_free'), (6, b'phymem_usage_active'), (7, b'phymem_usage_inactive'), (8, b'phymem_usage_buffers'), (9, b'phymem_usage_cached'), (10, b'swap_memory_total'), (11, b'swap_memory_used'), (12, b'swap_memory_free'), (13, b'swap_memory_percent'), (14, b'swap_memory_sin'), (15, b'swap_memory_sout'), (16, b'cached_phymem'), (17, b'disk_usage_systemdisk'), (18, b'disk_usage')])),
                ('parameter', models.CharField(default=b'', max_length=400, null=True, blank=True)),
                ('system_stat_variable', models.OneToOneField(to='pyscada.Variable')),
            ],
        ),
    ]

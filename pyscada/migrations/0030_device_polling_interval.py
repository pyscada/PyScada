# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0029_scaling_limit_input'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='polling_interval',
            field=models.FloatField(default=2.5, blank=True, choices=[(1, '1 Second'), (2.5, '2.5 Seconds'), (5, '5 Seconds'), (10, '10 Seconds'), (15, '15 Seconds'), (30, '30 Seconds'), (60, '1 Minute'), (150, '2.5 Mintues'), (300, '5 Minutes'), (360, '6 Minutes (10 times per Hour)'), (600, '10 Minutes'), (900, '15 Minutes'), (1800, '30 Minutes'), (3600, '1 Hour')]),
        ),
    ]

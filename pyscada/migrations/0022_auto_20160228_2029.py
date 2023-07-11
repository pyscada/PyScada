# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0021_auto_20160228_1643"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="variable",
            name="record",
        ),
        migrations.AddField(
            model_name="variable",
            name="cov_increment",
            field=models.FloatField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name="device",
            name="device_type",
            field=models.CharField(
                default="generic",
                max_length=400,
                choices=[
                    ("generic", "no Protocol"),
                    ("systemstat", "Local System Monitoring"),
                    ("modbus", "Modbus Device"),
                ],
            ),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0015_auto_20160215_1522"),
    ]

    operations = [
        migrations.AlterField(
            model_name="device",
            name="device_type",
            field=models.CharField(
                default="generic",
                max_length=400,
                choices=[
                    ("generic", "no Device"),
                    ("systemstat", "Local System Monitoring"),
                    ("modbus", "Modbus Device"),
                ],
            ),
        ),
    ]
